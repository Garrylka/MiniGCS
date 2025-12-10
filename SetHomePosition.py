from pymavlink import mavutil
import time


# Константы

DEFAULT_CONN_STRING = 'tcp:127.0.0.1:14550'     # Если MP и код на одном компе
REMOTE_CONN_STRING  = 'tcp:192.168.0.10:14550'  # IP компа с MP, настроен TCP IN 14550 одной строкой в MAVLink Mirror в MP

TARGET_SYSTEM  = 200    # ID дрона
TARGET_COMPONENT = 1    # ID автопилота

# HOME_POS_PTZ: 61.7829553, 34.3596839 - Петрозаводск
HOME_POSITION_PTZ = {"lat": 61.7829553, "lon": 34.3596839, "alt": 80}

SCALE_DEG = 1e7     # Коэффициент для преобразования географических координат в целое
SCALE_ALT = 1000    # Коэффициент для преобразования высоты в метрах в миллиметры


def set_home_position_to_mp(master, lat, lon, alt):
    """Отправка HOME_POSITION в Mission Planner"""
    master.mav.send(
        master.mav.home_position_encode(
            int(lat * SCALE_DEG),   # latitude (degrees*1.0e7)
            int(lon * SCALE_DEG),   # longitude (degrees*1.0e7)
            int(alt * SCALE_ALT),   # altitude (mm)
            0, 0, 0,                # x, y, z (local)
            [1, 0, 0, 0],           # q (unit quaternion)
            0, 0, 0,                # approach (local)
            0                       # time_usec
        )
    )
    print(f"Домашняя позиция отправлена в MP: Lat: {lat}, Lon: {lon}, Alt: {alt}м")
    print("\n2. Отправляю HEARTBEAT...")
    master.mav.heartbeat_send(6, 0, 0, 0, 0)


def send_home_position_to_mp_with_ack(master, lat, lon, alt, timeout=5):
    """Отправить HOME_POSITION и ждать подтверждения"""
    set_home_position_to_mp(master, lat, lon, alt)

    print("\n3. Слушаю 10 секунд...")
    messages = []

    for i in range(10):
        msg = master.recv_match(blocking=True, timeout=1)
        if msg:
            src = msg.get_srcSystem()
            mtype = msg.get_type()
            messages.append((src, mtype))
            print(f"   [{i + 1}] System {src}: {mtype}")
        else:
            print(f"   [{i + 1}] ...")

    # Анализ
    print("\n" + "=" * 50)
    print("АНАЛИЗ:")

    if not messages:
        print("НИЧЕГО не получено. MP не отвечает.")
        print("Но это нормально - MP может только принимать.")
    else:
        systems = set(src for src, _ in messages)
        print(f"Получены сообщения от систем: {systems}")

        if 1 in systems:
            print("✓ System 1 (дрон) отвечает - есть связь с SITL")
        if 255 in systems:
            print("✓ System 255 (MP) отвечает - MP отправляет ответы")
        if 200 in systems:
            print("? System 200 (ты) - эхо твоих сообщений")

    print("\nТеперь открой MP и проверь:")
    print("1. MAVLink Inspector - фильтруй по system 200")
    print("2. Должны быть HEARTBEAT и HOME_POSITION от 200")
    print("3. На карте - должна быть Home точка")


def set_home_position_to_fc(master, lat, lon, alt):
    """Отправка HOME_POSITION в Flight Controller"""
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,
        0,          # confirmation
        1,          # param1: 1=use current location, 0=use specified location
        0, 0, 0, 0, # не используются
        lat,        # param5: latitude
        lon,        # param6: longitude
        alt         # param7: altitude
    )
    print(f"Домашняя позиция отправлена в FC: Lat: {lat}, Lon: {lon}, Alt: {alt}м")


def set_home_position_to_gps(master, lat, lon, alt):
    """Дополнительно: отправляем GPS координаты для контекста"""
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
        print(f"Домашняя позиция отправлена в GPS: Lat: {lat}, Lon: {lon}, Alt: {alt}м")


def connect_to_autopilot(connection_string):
    """Подключение к автопилоту"""
    print(f"Подключаемся к автопилоту по адресу: {connection_string} ...")
    master = mavutil.mavlink_connection(connection_string,
                                        source_system=TARGET_SYSTEM, source_component=TARGET_COMPONENT)

    # Ждем ответа перед отправкой команд
    master.wait_heartbeat()
    print(f"Подключились к системе {master.target_system}, компонент {master.target_component}")

    return master


def main(connection_string, home_position):
    # Подключение (выберите нужный вариант)

    # Вариант 1: Прямо в Mission Planner (UDP)
    # print("Соединение с Mission Planner через UDP...")
    # master = mavutil.mavlink_connection('udpout:127.0.0.1:14550')

    # Вариант 2: К симулятору (SITL)
    # print("Соединение с  SITL...")
    # master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')

    # Вариант 3: К реальному дрону
    # print("Соединение по UART...")
    # master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)

    # Вариант 4: Создание собственного источника (самый надежный для Mission Planner)
    master = connect_to_autopilot(connection_string)

    # Отправляем домашнюю позицию в MP
    #set_home_position_to_mp(master, **home_position)
    status = send_home_position_to_mp_with_ack(master, **home_position)
    print(status)

    # Отправляем домашнюю позицию в FC
    #set_home_position_to_fc(master, **home_position)

    # Дополнительно: отправляем GPS координаты для контекста
    #set_home_position_to_gps(master, **home_position)
    '''
    try:
        while True:
            master.wait_heartbeat()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановлено")
    '''

if __name__ == "__main__":
    main(REMOTE_CONN_STRING, HOME_POSITION_PTZ)
    input()
