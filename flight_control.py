import time
from pymavlink import mavutil

TARGET_SYSTEM  = 200    # ID дрона
TARGET_COMPONENT = 1    # ID автопилота

SCALE_DEG = 1e7     # Коэффициент для преобразования географических координат в целое
SCALE_ALT = 1000    # Коэффициент для преобразования высоты в метрах в миллиметры

def connect_to_ardupilot(connection_string, target_system=TARGET_SYSTEM, target_component=TARGET_COMPONENT):
    """Подключение к ArduPilot"""
    print(f"Подключаемся к ArduPilot по адресу: {connection_string} ...")

    master = mavutil.mavlink_connection(connection_string,
                                        source_system=target_system, source_component=target_component)

    # Ждем ответа
    result = master.wait_heartbeat(timeout=1)
    if result is None:  # None будет в случае таймаута
        print("Ошибка подключения к ArduPilot!")
        return None
    print(f"Подключились к ArduPilot системе {master.target_system}, компонент {master.target_component}")

    return master


def disconnect_from_ardupilot(master):
    pass


def set_home(master: mavutil.mavlink_connection, lat, lon, alt, timeout=5):
    result = False
    print(f"Устанавливаем новые координаты Home.")
    # Команда установки home (param1=0 для specific location)
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0,
        0,  # param1: 1=use current location, 0=use specified location
        0, 0, 0,
        lat, lon, alt  # float degrees, float degrees, float meters AMSL
    )
    print(f"Домашняя позиция отправлена в GPS: Lat: {lat}, Lon: {lon}, Alt: {alt}м")

    # Ждём ACK
    msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
    if msg and msg.command == mavutil.mavlink.MAV_CMD_DO_SET_HOME:
        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("Новые координаты Home установились успешно!")
            result = True
        else:
            print(f"Ошибка при установки Home = {msg.result}")
    else:
        print("Нет ответа ACK!")


    # Дополнительно: отправьте home_position_encode для синхронизации с planner
    master.mav.send(master.mav.home_position_encode(
        int(lat*SCALE_DEG), int(lon*SCALE_DEG), int(alt*SCALE_ALT), 0, 0, 0, [1,0,0,0], 0, 0, 0, 0
    ))

    #Дополнительно: отправляем GPS координаты для контекста
    for i in range(10):
        master.mav.gps_raw_int_send(
            int(time.time() * 1000000), # time_usec
            3,                          # fix_type: 3=3D fix
            int(lat * SCALE_DEG),       # lat
            int(lon * SCALE_DEG),       # lon
            int(alt * SCALE_ALT),       # alt
            65535,                      # eph
            65535,                      # epv
            0,                          # vel
            0,                          # cog
            10                          # satellites_visible
        )
        time.sleep(0.1)

    return result


def set_mode(master: mavutil.mavlink_connection, mode_name: str, timeout: float = 5.0) -> None:
    """
    Универсальная функция смены режима полёта через SET_MODE
    - mode_name: строковое имя режима, например "GUIDED" или "AUTO".
    - mode_mapping() берётся из самого автопилота (через pymavlink), так что
      код не привязан к жёстко зашитым номерам custom_mode
    """
    mode_mapping = master.mode_mapping()
    if mode_mapping is None or mode_name not in mode_mapping:
        raise ValueError(f"Режим {mode_name} недоступен в mode_mapping()")

    mode_id = mode_mapping[mode_name]

    # Отправляем SET_MODE с флагом MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
    # и номером режима в custom_mode (flightmode number)
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

    # Небольшая пауза, чтобы автопилот успел сменить режим и прислать новый HEARTBEAT
    end_time = time.time() + timeout
    while time.time() < end_time:
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
        if msg is None:
            continue
        # можно реализовать проверку, что режим действительно сменился
        break


def set_mode_guided(master: mavutil.mavlink_connection) -> None:
    """
    Переводит Copter в режим GUIDED (управление с компьютера/скрипта)
    """
    set_mode(master, "GUIDED")


def set_mode_auto(master: mavutil.mavlink_connection) -> None:
    """
    Переводит Copter в режим AUTO для выполнения загруженной миссии
    """
    set_mode(master, "AUTO")


def send_command_arm(master: mavutil.mavlink_connection, force: bool = False) -> None:
    """
    ARM двигателей командой MAV_CMD_COMPONENT_ARM_DISARM
    """
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,  # param1: 1 = arm, 0 = disarm
        0 if not force else 21196,  # param2: 21196 => принудит. дизарм в полёте (для справки)
        0, 0, 0, 0, 0
    )


def send_command_disarm(master: mavutil.mavlink_connection, force: bool = False) -> None:
    """
    DISARM двигателей той же командой
    """
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,  # disarm
        0 if not force else 21196,
        0, 0, 0, 0, 0
    )


def send_command_takeoff(master: mavutil.mavlink_connection, alt_m: float) -> None:
    """
    Взлёт до alt_m с помощью MAV_CMD_NAV_TAKEOFF
    Предполагается, что Copter уже в режиме GUIDED и ARM
    """
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0,  # params 1–4 не используются Copter для обычного взлёта
        0,           # param5: lat, 0 = текущая
        0,           # param6: lon
        alt_m        # param7: высота (MAV_FRAME_GLOBAL_RELATIVE_ALT)
    )
    # Ждать фактическую высоту будет основная программа по данным DroneState


def send_command_land(master: mavutil.mavlink_connection) -> None:
    """
    Посадка: команда MAV_CMD_NAV_LAND (посадка в текущей точке)
    """
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,  #
        0,
        0, 0, 0, 0,  # параметры для Copter, 0 = посадка в текущей точке
        0, 0, 0
    )
    # Фактическое «приземлился и дизармился» также может проверяться через DroneState
