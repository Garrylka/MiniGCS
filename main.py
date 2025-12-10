import customtkinter as ctk
import os
import setup_gui as gui
from status_bar import StatusBar
from extended_mapview import ExtendedMapView
from flight_control import (
    connect_to_ardupilot, set_home, set_mode_guided, set_mode_auto,
    send_command_arm, send_command_disarm, send_command_takeoff, send_command_land
)
from mission_control import send_waypoints_to_drone


# Источники используемых GUI библиотек
#https://github.com/TomSchimansky/TkinterMapView
#https://customtkinter.tomschimansky.com/
#https://github.com/TomSchimansky/CustomTkinter

APP_NAME = 'Mini GCS'
APP_VERSION = 'v1.0.0'
APP_AUTHOR = 'Юрий Анатольевич Сафронов (garry1301@mail.ru)'
APP_COMPANY = 'HandMade'

WINDOW_TITLE = f'{APP_NAME} - {APP_VERSION}'
WINDOW_W = 800
WINDOW_H = 600
WINDOW_MAXIMIZED = False
FRAME_CTRL_WIDTH = 250

# PTZ HOME:     61.7829553, 34.3596839, ALT: 70
# PTZ SPARTAK:  61.7825445, 34.3673560, ALT: 60
HOME_POSITION_PTZ       = {"lat": 61.7829553, "lon": 34.3596839, "alt": 70}
HOME_POSITION_SPARTAK   = {"lat": 61.7825245, "lon": 34.3673200, "alt": 60}

MAP_INIT_POSITION_LAT = HOME_POSITION_SPARTAK['lat']
MAP_INIT_POSITION_LON = HOME_POSITION_SPARTAK['lon']

MAP_INIT_ZOOM = 15

MARKER_TEXT_PREFIX = 'WP'
MARKER_TEXT_COLOR = 'yellow'
MARKER_ICON_COLOR_IN = 'yellow'
MARKER_ICON_COLOR_OUT = 'red'

DRONE_TEXT_PREFIX = 'HP'
DRONE_TEXT_COLOR = 'blue'
DRONE_ICON_COLOR_IN = 'blue'
DRONE_ICON_COLOR_OUT = 'red'

PATH_CYCLIC = False
PATH_COLOR = 'red'
PATH_WIDTH = 3

DEFAULT_CONN_STRING = 'tcp:127.0.0.1:14550'     # Если MP и код на одном компе
REMOTE_CONN_STRING  = 'tcp:192.168.0.10:14550'  # IP компа с MP, настроен TCP IN 14550 одной строкой в MAVLink Mirror в MP

TARGET_SYSTEM  = 200    # ID дрона
TARGET_COMPONENT = 1    # ID автопилота

TAKEOFF_ALT = 10 # Взлетаем на относительную высоту в метрах


# Глобальная переменная marker для позиции Home дрона
drone_home_marker = None

# Глобальная переменная Список точек маршрута (lat, lon)
position_list = []

# Глобальная переменная для работы с MAVLink
master = None


# Создание основного окна Tkinter
window = ctk.CTk()

# Путь к базе данных offline-тайлов карты (offline tiles)
script_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(script_directory, "offline_tiles.db")

'''
# Создание меню приводит к неправильному расположению окна (уходит под Панель задач).
menu = Menu(window)
window.config(menu=menu)

# Добавление пунктов меню
file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Файл", menu=file_menu)
file_menu.add_command(label="Печать", command=lambda: print("Выбрана опция Печать"))
file_menu.add_separator()
file_menu.add_command(label="Выход", command=window.quit)
'''

window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=0) # statusbar

frame_top = ctk.CTkFrame(master=window, corner_radius=0)
frame_top.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")

frame_status = ctk.CTkFrame(master=window, height=30, corner_radius=0, fg_color=None)
frame_status.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

frame_ctrl = ctk.CTkFrame(master=frame_top, width=FRAME_CTRL_WIDTH, corner_radius=0, fg_color=None)
frame_ctrl.pack(side="left", fill="y")  # Фиксированная ширина из width=250
frame_ctrl.grid_columnconfigure(0, weight=1)  # Дочерние будут растягиваться по ширине

frame_map = ctk.CTkFrame(master=frame_top, corner_radius=0)
frame_map.pack(side="right", fill="both", expand=True)

# Создание статус-бара
status_bar = StatusBar(frame_status, height=28)  # height=28 чтобы влезло в frame_status высотой 30
status_bar.pack(padx=2, pady=2, fill='both')
status_bar.set_status("Это строка состояния!", "info")


# И используем grid для размещения дочерних элементов
#zoom_label = ctk.CTkLabel(frame_ctrl, text="Зум: ", height=40, font=("Arial", 12))
#zoom_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

conn_frame = ctk.CTkFrame(frame_ctrl, fg_color="transparent")
conn_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
conn_frame.grid_columnconfigure(0, weight=1)

conn_entry = ctk.CTkEntry(conn_frame, placeholder_text="Строка соединения...", font=("Arial", 10))
conn_entry.grid(row=0, column=0, sticky="ew", padx=5)
conn_button = ctk.CTkButton(conn_frame, text="🔌", width=40, fg_color=("gray70", "gray30"))
conn_button.grid(row=0, column=1)
conn_entry.delete(0, "end")
conn_entry.insert(0, REMOTE_CONN_STRING)


btn_send_home = ctk.CTkButton(frame_ctrl, text="SET HOME", height=40)
btn_send_home.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

btn_send_wp = ctk.CTkButton(frame_ctrl, text="SEND WP", height=40)
btn_send_wp.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

btn_send_guided = ctk.CTkButton(frame_ctrl, text="GUIDED", height=40)
btn_send_guided.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

btn_send_arm = ctk.CTkButton(frame_ctrl, text="ARM", height=40)
btn_send_arm.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

btn_send_takeoff = ctk.CTkButton(frame_ctrl, text="TAKEOFF", height=40)
btn_send_takeoff.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

btn_send_land = ctk.CTkButton(frame_ctrl, text="LAND", height=40)
btn_send_land.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

btn_send_disarm = ctk.CTkButton(frame_ctrl, text="DISARM", height=40)
btn_send_disarm.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

btn_send_auto = ctk.CTkButton(frame_ctrl, text="AUTO", height=40)
btn_send_auto.grid(row=8, column=0, padx=10, pady=5, sticky="ew")


#switch = ctk.CTkSwitch(frame_ctrl, text="Слои карты", height=40)
#switch.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# Зациклить полет
#checkbox_grid = ctk.CTkCheckBox(frame_ctrl, text="Зациклить полет", height=30, corner_radius=5)
#checkbox_grid.grid(row=4, column=0, padx=10, pady=5, sticky="w")

spacer = ctk.CTkFrame(frame_ctrl, fg_color="transparent")
spacer.grid(row=9, column=0, sticky="nsew")

# Настраиваем веса строк
frame_ctrl.grid_rowconfigure(9, weight=1)  # Заполнитель растягивается


# MAP
def debug_mouse_callback(lat, lon):
    if lat is not None:
        #print(f"Мышь над картой: {lat:.6f}, {lon:.6f}")
        status_bar.set_coordinates(lat, lon)
    else:
        #print("Мышь вне карты")
        pass

# Создание виджета карты
map_widget = ExtendedMapView(frame_map,
                             zoom_callback=lambda z: status_bar.set_zoom(z),
                             mouse_callback=debug_mouse_callback,
                             corner_radius=0, database_path=database_path)

'''
# example tile sever:
self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
self.map_widget.set_tile_server("http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.png")  # painting style
self.map_widget.set_tile_server("http://a.tile.stamen.com/toner/{z}/{x}/{y}.png")  # black and white
self.map_widget.set_tile_server("https://tiles.wmflabs.org/hikebike/{z}/{x}/{y}.png")  # detailed hiking
self.map_widget.set_tile_server("https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png")  # no labels
self.map_widget.set_tile_server("https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg")  # swisstopo map

# example overlay tile server
self.map_widget.set_overlay_tile_server("http://tiles.openseamap.org/seamark//{z}/{x}/{y}.png")  # sea-map overlay
self.map_widget.set_overlay_tile_server("http://a.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png")  # railway infrastructure
'''
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=20)  # google satellite)
map_widget.pack(fill="both", expand=True)

# Установка начальной позиции карты
map_widget.set_position(MAP_INIT_POSITION_LAT, MAP_INIT_POSITION_LON)
map_widget.set_zoom(MAP_INIT_ZOOM)


# Функция для добавления маркера на карту
def add_marker_event_handler(position):
    '''
    if len(position_list) == 0:
        position_list.append(position)
        position_list.append(position)
    else:
        if PATH_CYCLIC:
            position_list.insert(-1, position)
        else:
            position_list.append(position)
    '''
    position_list.append(position)
    #count = len(position_list) - 1
    count = len(position_list)
    map_widget.set_marker(position[0], position[1],
                   text=MARKER_TEXT_PREFIX + str(count), text_color=MARKER_TEXT_COLOR,
                   marker_color_circle= MARKER_ICON_COLOR_IN, marker_color_outside=MARKER_ICON_COLOR_OUT,
                   command=marker_click_event_handler)
    if count > 1:
        map_widget.delete_all_path()
        map_widget.set_path(position_list, color=PATH_COLOR, width=PATH_WIDTH)


def marker_click_event_handler(marker):
    #last_index = -2 if PATH_CYCLIC else -1
    last_index = -1
    if marker.position != position_list[last_index]: return
    map_widget.delete(marker)
    map_widget.delete_all_path()

    #if len(position_list) == 2:
    #    position_list.clear()
    #else:
    position_list.pop(last_index)
    if len(position_list) > 1:
        map_widget.set_path(position_list, color=PATH_COLOR, width=PATH_WIDTH)


def delete_all_markers_event_handler():
    global drone_home_marker
    position_list.clear()
    position = drone_home_marker.position
    map_widget.delete_all_marker()
    map_widget.delete_all_path()
    drone_home_marker = draw_drone_home_position(position)


# Отрисовка HOME дрона на карте
def draw_drone_home_position(position):
    return map_widget.set_marker(position[0], position[1],
                          text=DRONE_TEXT_PREFIX, text_color=DRONE_TEXT_COLOR,
                          marker_color_circle=DRONE_ICON_COLOR_IN, marker_color_outside=DRONE_ICON_COLOR_OUT,
                          command=drone_home_click_event_handler)


def set_drone_home_event_handler(position):
    drone_home_marker.set_position(position[0], position[1])
    '''
    global drone_home_marker
    drone_home_marker.delete()
    drone_home_marker = draw_drone_home_position(position)
    '''

def drone_home_click_event_handler(marker):
    pass


# Привязка события ЛКМ к функции добавления маркера
#map.add_left_click_map_command(add_marker_event_handler)

# Привязка события ПКМ к функции добавления маркера
map_widget.add_right_click_menu_command(label="Добавить путевую точку",
                                        command=add_marker_event_handler, pass_coords=True)

# Привязка события ПКМ к функции установки позиции HOME дрона
map_widget.add_right_click_menu_command(label="Установить HOME здесь",
                                        command=set_drone_home_event_handler, pass_coords=True)

# Привязка события ПКМ удаления всех маркеров
map_widget.add_right_click_menu_command(label="Удалить все путевые точки",
                                        command=delete_all_markers_event_handler)


# Для maximize окна надо вызывать последним, используется задержка after().
gui.setup_window(window, WINDOW_TITLE, WINDOW_W, WINDOW_H, WINDOW_MAXIMIZED)

# Отрисовка HOME дрона при инициализации программы
drone_home_marker = draw_drone_home_position((MAP_INIT_POSITION_LAT, MAP_INIT_POSITION_LON))


def get_connection_string():
    """Получить строку подключения с проверкой"""
    conn_text = conn_entry.get().strip()

    if conn_text:  # Если не пустая
        return conn_text
    else:
        # Значение по умолчанию
        return DEFAULT_CONN_STRING


def connect_mavlink_advanced():
    global master
    #current_icon = conn_button.cget("text")
    #if current_icon == "🔌":
    if master is None:
        connection_string = get_connection_string()
        status_bar.set_status(f"Подключаемся к Ardupilot по адресу: {connection_string} ...")
        master = connect_to_ardupilot(connection_string)
        if master is None:
            status_bar.set_status("Ошибка подключения!", "error")
        else:
            status_bar.set_status(f"Подключились к системе {master.target_system}, компонент {master.target_component}", "success")
            conn_button.configure(text="⚡", fg_color=("green", "darkgreen"))
    else:
        conn_button.configure(text="🔌", fg_color=("gray70", "gray30"))
        status_bar.set_status("Отключились от Ardupilot!", "info")
        master.close()
        master = None

conn_button.configure(command=connect_mavlink_advanced)


def send_home_advanced():
    if master:
        status_bar.set_status(f"Устанавливаем новые координаты Home.")
        home_position = HOME_POSITION_SPARTAK
        result = set_home(master, **home_position)
        if result:
            status_bar.set_status("Новые координаты Home установились успешно!", "success")
        else:
            status_bar.set_status("Ошибка при установки Home", "error")
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_home.configure(command=send_home_advanced)

def send_guided_advanced():
    if master:
        status_bar.set_status(f"Устанавливаем режим GUIDED.")
        set_mode_guided(master)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_guided.configure(command=send_guided_advanced)

def send_wp_advanced():
    if len(position_list) == 0:
        status_bar.set_status("Нет маршрутных точек для полета!", "error")
        return
    if master:
        status_bar.set_status(f"Отправляем точки маршрута.")
        result = send_waypoints_to_drone(master, position_list, TAKEOFF_ALT)
        if result:
            print("Маршрут загружен в Ardupilot! Теперь можно нажать AUTO!")
        else:
            print("Не удалось отправить маршрут!")
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_wp.configure(command=send_wp_advanced)

def send_arm_advanced():
    if master:
        status_bar.set_status(f"Отправляем команду ARM.")
        send_command_arm(master)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_arm.configure(command=send_arm_advanced)

def send_takeoff_advanced():
    if master:
        status_bar.set_status(f"Отправляем команду TAKEOFF.")
        send_command_takeoff(master, TAKEOFF_ALT)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_takeoff.configure(command=send_takeoff_advanced)

def send_land_advanced():
    if master:
        status_bar.set_status(f"Отправляем команду LAND.")
        send_command_land(master)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_land.configure(command=send_land_advanced)

def send_disarm_advanced():
    if master:
        status_bar.set_status(f"Отправляем команду DISARM.")
        send_command_disarm(master)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_disarm.configure(command=send_disarm_advanced)

def send_auto_advanced():
    if master:
        status_bar.set_status(f"Устанавливаем режим AUTO.")
        set_mode_auto(master)
    else:
        status_bar.set_status("Нет подключения к Ardupilot!", "error")

btn_send_auto.configure(command=send_auto_advanced)


# Запуск главного цикла Tkinter
window.mainloop()
