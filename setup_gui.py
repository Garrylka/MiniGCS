'''
    Настройка GUI.
'''

# Не учитывается наличие и высота Панели задач!
def bad_maximize_window(window):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Устанавливаем размеры окна, вычитая высоту панели задач
    window.geometry(f"{screen_width}x{screen_height}+0+0")


# Расположение окна в центре экрана (без учета высоты Панели задач)
def center_window(window, width, height):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Вычисляем координаты для размещения окна в центре
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Устанавливаем размеры и положение окна
    window.geometry(f'{width}x{height}+{x}+{y}')


def setup_window(window, title, width, height, maximized):
    window.title(title)
    window.minsize(width, height)

    # Устанавливаем состояние окна в "развернутое"
    def maximize_window():
        window.state('zoomed')

    if maximized:
        #window.attributes("-fullscreen", fullscreen) # это прям во весь экран :)
        #bad_maximize_window(window) # кривовато: слева полоса рабочего стола видна, Панель задач не учитывается!
        #window.attributes('-zoomed', True) # нет такого атрибута!

        window.after(100, maximize_window)
    else:
        center_window(window, width, height)


