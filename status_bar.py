import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Получаем высоту из kwargs или ставим по умолчанию
        bar_height = kwargs.pop('height', 30)

        # Сразу задаем высоту при создании родительского фрейма
        super().__init__(master, height=bar_height, **kwargs)

        # Отключаем авто-размер
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Настройка внешнего вида
        self.configure(
            corner_radius=4,
            border_width=2,
            border_color=("gray70", "gray30"),
            fg_color=("gray85", "gray25")
        )

        # Создаем внутренний фрейм (для объемного эффекта)
        inner_frame = ctk.CTkFrame(
            self,
            fg_color=("gray92", "gray24"),
            height=bar_height - 4  # Чуть меньше внешнего
        )
        inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
        inner_frame.pack_propagate(False)

        # Теперь используем grid для размещения нескольких ячеек
        inner_frame.grid_columnconfigure(0, weight=10)  # Основной текст (3 части)
        inner_frame.grid_columnconfigure(1, weight=2)  # Lat (1 часть)
        inner_frame.grid_columnconfigure(2, weight=2)  # Lon (1 часть)
        inner_frame.grid_columnconfigure(3, weight=1)  # Zoom (1 часть)
        inner_frame.grid_rowconfigure(0, weight=1)  # Одна строка

        # Создаем отдельные "ячейки" статус-бара
        self._create_cells(inner_frame, bar_height)

        # Цвета для разных типов статусов
        self.status_colors = {
            "info": ("black", "white"),
            "success": ("green", "lightgreen"),
            "warning": ("orange", "yellow"),
            "error": ("red", "pink"),
            "loading": ("blue", "lightblue")
        }

        # Инициализируем значения
        self.set_coordinates(0.0, 0.0)
        self.set_zoom(0)
        self.set_status("Это строка состояния!", "info")

    def _create_cells(self, parent, bar_height):
        """Создаем отдельные ячейки статус-бара"""

        # 1. Ячейка для основного текста статуса (левый блок)
        self.status_cell = self._create_cell(
            parent,
            row=0,
            column=0,
            text="Готово",
            padx=1
        )

        # 2. Ячейка для широты (Lat)
        self.lat_cell = self._create_cell(
            parent,
            row=0,
            column=1,
            text="Lat: 0.0000000",
            bg_color=("gray85", "gray30"),  # Немного темнее для выделения
            padx=1
        )

        # 3. Ячейка для долготы (Lon)
        self.lon_cell = self._create_cell(
            parent,
            row=0,
            column=2,
            text="Lon: 0.0000000",
            bg_color=("gray85", "gray30"),
            padx=1
        )

        # 4. Ячейка для зума
        self.zoom_cell = self._create_cell(
            parent,
            row=0,
            column=3,
            text="Zoom: 0",
            bg_color=("gray88", "gray28"),
            padx=1
        )

    def _create_cell(self, parent, row, column, text, bg_color=None, padx=5):
        """Создает одну ячейку статус-бара с объемным эффектом"""
        if bg_color is None:
            bg_color = ("gray90", "gray22")

        # Основной фрейм ячейки
        cell_frame = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=3,
            border_width=1,
            border_color=("gray60", "gray40")
        )
        cell_frame.grid(row=row, column=column, sticky="nsew", padx=padx, pady=2)
        cell_frame.grid_propagate(False)

        # Label внутри ячейки
        label = ctk.CTkLabel(
            cell_frame,
            text=text,
            font=("Consolas", 10),
            anchor="center"
        )
        label.pack(fill="both", expand=True, padx=5, pady=2)

        return label

    def set_status(self, text, status_type="info"):
        """Установить основной текст статуса"""
        self.status_cell.configure(text=text)
        if status_type in self.status_colors:
            self.status_cell.configure(text_color=self.status_colors[status_type])

    def set_coordinates(self, lat, lon):
        """Установить координаты"""
        self.lat_cell.configure(text=f"Lat: {lat:.7f}")
        self.lon_cell.configure(text=f"Lon: {lon:.7f}")

    def set_zoom(self, zoom_level):
        """Установить уровень зума"""
        self.zoom_cell.configure(text=f"Zoom: {round(zoom_level)}")

        # Меняем цвет в зависимости от уровня зума
        if zoom_level < 14:
            color = ("blue", "lightblue")
        elif zoom_level < 16:
            color = ("green", "lightgreen")
        elif zoom_level < 18:
            color = ("orange", "yellow")
        else:
            color = ("red", "pink")
        self.zoom_cell.configure(text_color=color)

    def update_all(self, status_text, status_type, lat, lon, zoom):
        """Обновить все поля сразу"""
        self.set_status(status_text, status_type)
        self.set_coordinates(lat, lon)
        self.set_zoom(zoom)


# Альтернативный вариант с более выраженным объемным эффектом
class StatusBarEnhanced(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        bar_height = kwargs.pop('height', 32)
        super().__init__(master, height=bar_height, **kwargs)

        self.pack_propagate(False)
        self.grid_propagate(False)

        # Более выраженный объемный эффект
        self.configure(
            corner_radius=6,
            border_width=3,
            border_color=(
                ("#e0e0e0", "#404040"),  # Левый-верхний светлый/темный
                ("#a0a0a0", "#202020")  # Правый-нижний темный/очень темный
            ),
            fg_color=("gray90", "gray20")
        )

        # Внутренний контейнер
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=3, pady=3)

        # Используем grid с весами
        inner.grid_columnconfigure(0, weight=10)  # Статус
        inner.grid_columnconfigure(1, weight=2)  # Lat
        inner.grid_columnconfigure(2, weight=2)  # Lon
        inner.grid_columnconfigure(3, weight=1)  # Zoom
        inner.grid_rowconfigure(0, weight=1)

        # Создаем ячейки с рельефным эффектом
        self.cells = {}
        columns = [
            ("status", "Готов", 0, ("gray95", "gray15")),
            ("lat", "Lat: --", 1, ("#e8f4fd", "#1a3c5a")),
            ("lon", "Lon: --", 2, ("#e8f4fd", "#1a3c5a")),
            ("zoom", "Zoom: --", 3, ("#f0f8ff", "#2a4c6a"))
        ]

        for name, text, col, bg_color in columns:
            cell = self._create_relief_cell(inner, text, col, bg_color)
            self.cells[name] = cell

        # Цвета статусов
        self.status_colors = {
            "info": ("#0066cc", "#80b3ff"),
            "success": ("#2e7d32", "#a5d6a7"),
            "warning": ("#f57c00", "#ffcc80"),
            "error": ("#c62828", "#ef9a9a"),
            "loading": ("#6a1b9a", "#ce93d8")
        }

    def _create_relief_cell(self, parent, text, column, bg_color):
        """Создает ячейку с рельефным эффектом"""
        # Фоновая "тень"
        shadow = ctk.CTkFrame(
            parent,
            fg_color=("gray70", "gray40"),
            corner_radius=4
        )
        shadow.grid(row=0, column=column, sticky="nsew", padx=(2, 2), pady=2)

        # Основная ячейка (выпуклая)
        main_cell = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=4,
            border_width=1,
            border_color=("white", "gray50")
        )
        main_cell.grid(row=0, column=column, sticky="nsew", padx=(0, 2), pady=2)
        main_cell.grid_propagate(False)

        # Label
        label = ctk.CTkLabel(
            main_cell,
            text=text,
            font=("Consolas", 10, "bold"),
            anchor="center"
        )
        label.pack(fill="both", expand=True, padx=8, pady=3)

        return label

    def set_status(self, text, status_type="info"):
        self.cells["status"].configure(text=text)
        if status_type in self.status_colors:
            self.cells["status"].configure(text_color=self.status_colors[status_type])

    def set_coordinates(self, lat, lon):
        self.cells["lat"].configure(text=f"Lat: {lat:.7f}")
        self.cells["lon"].configure(text=f"Lon: {lon:.7f}")

    def set_zoom(self, zoom_level):
        self.cells["zoom"].configure(text=f"Zoom: {zoom_level}")

        # Динамический цвет для зума
        colors = [
            (0, 5, ("#1e88e5", "#90caf9")),  # Синий
            (5, 10, ("#43a047", "#a5d6a7")),  # Зеленый
            (10, 15, ("#fb8c00", "#ffb74d")),  # Оранжевый
            (15, 20, ("#e53935", "#ef9a9a"))  # Красный
        ]

        for min_z, max_z, color in colors:
            if min_z <= zoom_level < max_z:
                self.cells["zoom"].configure(text_color=color)
                break


# Минималистичный вариант
class CompactStatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        bar_height = kwargs.pop('height', 28)
        super().__init__(master, height=bar_height, **kwargs)

        self.grid_propagate(False)

        # Простой стиль
        self.configure(
            corner_radius=0,
            border_width=1,
            border_color=("gray60", "gray40"),
            fg_color=("gray88", "gray22")
        )

        # Grid с равными колонками
        self.grid_columnconfigure(0, weight=2)  # Статус
        self.grid_columnconfigure(1, weight=1)  # Координаты
        self.grid_columnconfigure(2, weight=1)  # Zoom
        self.grid_rowconfigure(0, weight=1)

        # Создаем метки
        self.status_label = ctk.CTkLabel(
            self,
            text="Готов",
            font=("Segoe UI", 9),
            anchor="w",
            padx=10
        )
        self.status_label.grid(row=0, column=0, sticky="nsew")

        self.coords_label = ctk.CTkLabel(
            self,
            text="55.7558, 37.6173",
            font=("Consolas", 9),
            anchor="center"
        )
        self.coords_label.grid(row=0, column=1, sticky="nsew", padx=5)

        self.zoom_label = ctk.CTkLabel(
            self,
            text="Zoom: 10",
            font=("Consolas", 9, "bold"),
            anchor="center",
            padx=10
        )
        self.zoom_label.grid(row=0, column=2, sticky="nsew")

    def set_status(self, text, status_type="info"):
        self.status_label.configure(text=text)

    def set_coordinates(self, lat, lon):
        self.coords_label.configure(text=f"{lat:.7f}, {lon:.7f}")

    def set_zoom(self, zoom_level):
        self.zoom_label.configure(text=f"Zoom: {zoom_level}")


'''
# Пример использования
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x100")

    frame_status = ctk.CTkFrame(app, height=32, fg_color=None)
    frame_status.pack(fill="x", padx=10, pady=10)
    frame_status.pack_propagate(False)

    # Используйте один из вариантов:
    # status_bar = StatusBar(frame_status, height=30)
    status_bar = StatusBarEnhanced(frame_status, height=30)
    # status_bar = CompactStatusBar(frame_status, height=28)

    status_bar.pack(fill="both", expand=True)

    # Тестируем
    status_bar.set_status("Карта загружена", "success")
    status_bar.set_coordinates(55.7558, 37.6173)
    status_bar.set_zoom(12)

    app.mainloop()
'''