from typing import Any

from tkintermapview import TkinterMapView


class ExtendedMapView(TkinterMapView):
    def __init__(self, *args, **kwargs):
        self.zoom_callback = kwargs.pop('zoom_callback', None)
        self.mouse_callback = kwargs.pop('mouse_callback', None)

        super().__init__(*args, **kwargs)

        # Троттлинг для мыши
        self._mouse_timer = None
        self._last_mouse_coords = None

        if self.mouse_callback:
            # ПРИВЯЗЫВАЕМ К CANVAS, А НЕ К САМОМУ ВИДЖЕТУ!
            self.canvas.bind("<Motion>", self._on_mouse_move)  # ← ИЗМЕНИЛ ЭТУ СТРОКУ

    def set_zoom(self, zoom: int, relative_pointer_x: float = 0.5, relative_pointer_y: float = 0.5):
        super().set_zoom(zoom, relative_pointer_x, relative_pointer_y)
        if self.zoom_callback:
            self.zoom_callback(zoom)

    def _on_mouse_move(self, event):
        """Движение мыши с троттлингом"""
        # Сохраняем координаты
        self._last_mouse_coords = (event.x, event.y)

        if self._mouse_timer:
            self.after_cancel(self._mouse_timer)

        # Ставим таймер
        self._mouse_timer = self.after(50, self._process_mouse_move)

    def _process_mouse_move(self):
        """Обработка движения мыши после задержки"""
        if self._last_mouse_coords:
            x, y = self._last_mouse_coords
            try:
                lat, lon = self.convert_canvas_coords_to_decimal_coords(x, y)
                # Отладочный вывод
                #print(f"Мышь: x={x}, y={y} -> lat={lat:.6f}, lon={lon:.6f}")
                if self.mouse_callback:
                    self.mouse_callback(lat, lon)
            except Exception as e:
                #print(f"Ошибка конвертации: {e}")
                if self.mouse_callback:
                    self.mouse_callback(None, None)

        self._mouse_timer = None


'''
class ExtendedMapView(TkinterMapView):
    def __init__(self, *args, **kwargs):
        self.zoom_callback = kwargs.pop('zoom_callback', None)
        super().__init__(*args, **kwargs)

    def set_zoom(self, zoom: int, relative_pointer_x: float = 0.5, relative_pointer_y: float = 0.5):
        """Переопределяем метод изменения зума"""
        super().set_zoom(zoom, relative_pointer_x, relative_pointer_y)
        if self.zoom_callback:
            self.zoom_callback(zoom)
'''