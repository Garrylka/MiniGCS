from pymavlink import mavutil
import time

# Константы

DEFAULT_CONN_STRING = 'tcp:127.0.0.1:14550'     # Если MP и код на одном компе
REMOTE_CONN_STRING  = 'tcp:192.168.0.10:14550'  # IP компа с MP, настроен TCP IN 14550 одной строкой в MAVLink Mirror в MP

TARGET_SYSTEM  = 200    # ID дрона
TARGET_COMPONENT = 1    # ID автопилота

# PTZ HOME:     61.7829553, 34.3596839, ALT: 70
# PTZ SPARTAK:  61.7825445, 34.3673560, ALT: 60
HOME_POSITION_PTZ       = {"lat": 61.7829553, "lon": 34.3596839, "alt": 70}
HOME_POSITION_SPARTAK   = {"lat": 61.7825445, "lon": 34.3673560, "alt": 60}

SCALE_DEG = 1e7     # Коэффициент для преобразования географических координат в целое
SCALE_ALT = 1000    # Коэффициент для преобразования высоты в метрах в миллиметры


############################################################################################

lat = HOME_POSITION_PTZ['lat']
lon = HOME_POSITION_PTZ['lon']
alt = HOME_POSITION_PTZ['alt']


master = mavutil.mavlink_connection(REMOTE_CONN_STRING)  # Ваш порт
master.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))


# Команда установки home (param1=0 для specific location)
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0,
    0,  # use_current_location=False
    0, 0, 0,
    lat, lon, alt  # float degrees, float degrees, float meters AMSL
)


# Ждём ACK
msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
if msg and msg.command == mavutil.mavlink.MAV_CMD_DO_SET_HOME:
    if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("Home set successfully!")
    else:
        print(f"Failed: result={msg.result}")
else:
    print("No ACK received")


# Опционально: отправьте home_position_encode для синхронизации с planner
master.mav.send(master.mav.home_position_encode(
    int(lat*SCALE_DEG), int(lon*SCALE_DEG), int(alt*SCALE_ALT), 0, 0, 0, [1,0,0,0], 0, 0, 0, 0
))
