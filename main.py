import tkinter as tk
import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import Menu
import setup_gui as gui

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


# Храним позицию HOME дрона для отрисовки на карте
#drone_home_position = HOME_POSITION_SPARTAK.copy()

# Создание основного окна Tkinter
window = ctk.CTk()

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

frame_top.grid_columnconfigure(0, weight=0)
frame_top.grid_columnconfigure(1, weight=1)
frame_top.grid_rowconfigure(0, weight=1)

frame_ctrl = ctk.CTkFrame(master=frame_top, width=200, corner_radius=0, fg_color=None)
frame_ctrl.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

frame_map = ctk.CTkFrame(master=frame_top, corner_radius=0)
frame_map.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")


# Создание виджета карты
#map = tkintermapview.TkinterMapView(window, width=800, height=600, corner_radius=0)
map_widget = TkinterMapView(frame_map, corner_radius=0)
map_widget.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")


# Создание статус-бара
status_bar = ctk.CTkLabel(frame_status, text="", corner_radius=0)
status_bar.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")

# Функция для обновления статус-бара
def update_status(message):
    status_bar.config(text=message)



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

#map_widget.place(x=0, y=0)
#map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # Хз?
map_widget.pack(fill="both", expand=True)


# Установка начальной позиции карты
#map.set_position(61.7829553, 34.3596839, marker=True) # Добавляет маркер на карту, не надо.
map_widget.set_position(MAP_INIT_POSITION_LAT, MAP_INIT_POSITION_LON)
map_widget.set_zoom(MAP_INIT_ZOOM)

'''
marker_3 = map.set_marker(61.7829553, 34.3596839, text="Tower", text_color="green", 
    marker_color_circle="black", marker_color_outside="gray40", font=("Helvetica Bold", 24))
'''

# Список точек маршрута (lat, lon)
position_list = []


# Функция для добавления маркера на карту
def add_marker_event_handler(position):
    if len(position_list) == 0:
        position_list.append(position)
        position_list.append(position)
    else:
        if PATH_CYCLIC:
            position_list.insert(-1, position)
        else:
            position_list.append(position)

    count = len(position_list) - 1
    map_widget.set_marker(position[0], position[1],
                   text=MARKER_TEXT_PREFIX + str(count), text_color=MARKER_TEXT_COLOR,
                   marker_color_circle= MARKER_ICON_COLOR_IN, marker_color_outside=MARKER_ICON_COLOR_OUT,
                   command=marker_click_event_handler)

    map_widget.delete_all_path()
    map_widget.set_path(position_list, color=PATH_COLOR, width=PATH_WIDTH)


def marker_click_event_handler(marker):
    last_index = -2 if PATH_CYCLIC else -1

    if marker.position != position_list[last_index]: return

    map_widget.delete(marker)
    map_widget.delete_all_path()

    if len(position_list) == 2:
        position_list.clear()
    else:
        position_list.pop(last_index)
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

# Запуск главного цикла Tkinter
window.mainloop()
