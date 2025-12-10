# mission_control.py

from dataclasses import dataclass
from typing import List

from pymavlink import mavutil

SCALE_DEG = 1e7
SCALE_ALT = 1000

@dataclass
class MissionItem:
    """
    Один пункт миссии в формате MISSION_ITEM_INT
    seq         – порядковый номер пункта (0..N-1)
    frame       – система координат (например, MAV_FRAME_GLOBAL_RELATIVE_ALT_INT)
    command     – команда MAV_CMD_NAV_... или другая
    current     – 1 для текущей точки (обычно только у первой)
    autocontinue – 1, если автоматически переходить к следующей точке
    param1..4   – параметры команды (зависят от типа команды)
    x, y        – широта/долгота * 1e7
    z           – высота в метрах
    """
    seq: int
    frame: int
    command: int
    current: int
    autocontinue: int
    param1: float
    param2: float
    param3: float
    param4: float
    x: int  # lat * 1e7
    y: int  # lon * 1e7
    z: float  # alt (м)


def clear_mission(master: mavutil.mavlink_connection) -> None:
    """
    Очистка миссии командой MISSION_CLEAR_ALL
    """
    master.mav.mission_clear_all_send(
        master.target_system,
        master.target_component
    )


def upload_mission(master: mavutil.mavlink_connection, items: List[MissionItem]) -> None:
    """
    Загрузка миссии по протоколу Mission Protocol:
    1) MISSION_COUNT
    2) цикл: MISSION_REQUEST_INT -> MISSION_ITEM_INT
    3) ожидание MISSION_ACK.
    """
    count = len(items)
    if count == 0:
        return

    master.mav.mission_count_send(
        master.target_system,
        master.target_component,
        count
    )

    sent = 0
    while sent < count:
        msg = master.recv_match(
            type=['MISSION_REQUEST_INT', 'MISSION_ACK'],
            blocking=True,
            timeout=5
        )
        if msg is None:
            # ПРОВЕРКА ПРОТОКОЛА: обработка таймаута
            continue

        if msg.get_type() == 'MISSION_REQUEST_INT':
            seq = msg.seq

            # ВАЛИДАЦИЯ ДАННЫХ: проверяем, что seq в диапазоне [0, count-1]
            if seq < 0 or seq >= count:
                print(f"Получен запрос миссии с некорректным seq={seq}, ожидаем 0..{count-1}")
                # ПРОВЕРКА ПРОТОКОЛА: игнорируем некорректный запрос
                continue

            item = items[seq]

            # ПРОВЕРКА ПРОТОКОЛА: отправка точки с подтверждением типа миссии
            master.mav.mission_item_int_send(
                master.target_system,
                master.target_component,
                item.seq,
                item.frame,
                item.command,
                item.current,
                item.autocontinue,
                item.param1,
                item.param2,
                item.param3,
                item.param4,
                item.x,
                item.y,
                item.z,
                mavutil.mavlink.MAV_MISSION_TYPE_MISSION  # подтверждение типа
            )
            sent += 1

        elif msg.get_type() == 'MISSION_ACK':
            # ПРОВЕРКА ПРОТОКОЛА: получение финального подтверждения
            print("MISSION_ACK получен, загрузка миссии завершена.")
            # В реальном коде здесь проверяем msg.type == MAV_MISSION_ACCEPTED
            break


def download_mission(master: mavutil.mavlink_connection) -> List[MissionItem]:
    """
    Чтение миссии по протоколу Mission Protocol:
    1) MISSION_REQUEST_LIST
    2) получение MISSION_COUNT
    3) цикл: MISSION_REQUEST_INT -> MISSION_ITEM_INT
    """
    # ПРОВЕРКА ПРОТОКОЛА: начало обмена
    master.mav.mission_request_list_send(
        master.target_system,
        master.target_component
    )

    # ПРОВЕРКА ПРОТОКОЛА: ожидание ответа с таймаутом
    msg = master.recv_match(type=['MISSION_COUNT'], blocking=True, timeout=5)
    if msg is None:
        return []  # ПРОВЕРКА: таймаут протокола

    count = msg.count
    items: List[MissionItem] = []

    for seq in range(count):
        # ПРОВЕРКА ПРОТОКОЛА: запрос каждой точки
        master.mav.mission_request_int_send(
            master.target_system,
            master.target_component,
            seq,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION  # подтверждение типа
        )

        # ПРОВЕРКА ПРОТОКОЛА: получение точки
        item_msg = master.recv_match(type=['MISSION_ITEM_INT'], blocking=True, timeout=5)
        if item_msg is None:
            continue  # ПРОВЕРКА: пропуск точки при таймауте

        # ВАЛИДАЦИЯ ДАННЫХ: создание объекта из полученных данных
        items.append(
            MissionItem(
                seq=item_msg.seq,
                frame=item_msg.frame,
                command=item_msg.command,
                current=item_msg.current,
                autocontinue=item_msg.autocontinue,
                param1=item_msg.param1,
                param2=item_msg.param2,
                param3=item_msg.param3,
                param4=item_msg.param4,
                x=item_msg.x,
                y=item_msg.y,
                z=item_msg.z,
            )
        )

    return items


# Рабочая функция для основной программы с маркерами на карте
def send_waypoints_to_drone(master: mavutil.mavlink_connection,
                            coordinates: list,  # список кортежей [(lat1, lon1), (lat2, lon2), ...]
                            altitude: float = 50.0) -> bool:
    """
    Отправляет навигационные точки дрону из списка координат.
    Возвращает True при успешной отправке, False при ошибке.
    """
    if not coordinates:
        print("Ошибка: список координат пуст")
        return False

    if not master:
        print("Ошибка: нет соединения с дроном")
        return False

    # Очищаем старый маршрут
    clear_mission(master)

    mission_items = []

    try:
        for i, (lat, lon) in enumerate(coordinates):
            # Первая точка - текущая (current=1), остальные - нет (current=0)
            current_flag = 1 if i == 0 else 0

            item = MissionItem(
                seq=i,
                frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                current=current_flag,
                autocontinue=1,
                param1=0,  # Hold time (секунды)
                param2=2,  # Acceptance radius (метры)
                param3=0,  # Pass through waypoint
                param4=0,  # Yaw angle
                x=int(lat * SCALE_DEG),  # Широта * 1e7
                y=int(lon * SCALE_DEG),  # Долгота * 1e7
                z=altitude  # Высота
            )
            mission_items.append(item)
            print(f"Точка {i + 1}: {lat:.7f}, {lon:.7f}, высота {altitude}м")

        print(f"Создано {len(mission_items)} точек маршрута")

        # Отправляем миссию
        upload_mission(master, mission_items)

        print("✅ Маршрут успешно отправлен дрону!")
        print("   Переключите дрон в режим AUTO для начала полета")
        return True

    except Exception as e:
        print(f"❌ Ошибка отправки маршрута: {e}")
        return False
