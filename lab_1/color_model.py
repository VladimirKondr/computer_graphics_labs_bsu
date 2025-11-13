from color_utils import rgb_to_cmyk, cmyk_to_rgb, rgb_to_hsv, hsv_to_rgb, rgb_to_hex

class ColorModel:
    def __init__(self):
        self._observers = []
        self._r, self._g, self._b = 255, 0, 0
        self._c, self._m, self._y, self._k = (0, 0, 0, 0)
        self._h, self._s, self._v = (0, 0, 0)
        self._hex = "#FF0000"
        self.update_from_rgb(self._r, self._g, self._b)

    def add_observer(self, observer):
        self._observers.append(observer)

    def _notify(self, source_observer=None):
        for observer in self._observers:
            if observer != source_observer:
                observer.update_from_model()
    
    def get_rgb(self): return self._r, self._g, self._b
    def get_cmyk(self): return self._c, self._m, self._y, self._k
    def get_hsv(self): return self._h, self._s, self._v
    def get_hex(self): return self._hex

    def update_from_rgb(self, r, g, b, source=None):
        r, g, b = int(round(r)), int(round(g)), int(round(b))

        self._r, self._g, self._b = r, g, b
        self._c, self._m, self._y, self._k = rgb_to_cmyk(r, g, b)
        self._h, self._s, self._v = rgb_to_hsv(r, g, b)
        self._hex = rgb_to_hex(r, g, b)
        self._notify(source)

    def update_from_cmyk(self, c, m, y, k, source=None):
        c, m, y, k = int(round(c)), int(round(m)), int(round(y)), int(round(k))

        self._c, self._m, self._y, self._k = c, m, y, k
        self._r, self._g, self._b = cmyk_to_rgb(c, m, y, k)
        self._h, self._s, self._v = rgb_to_hsv(self._r, self._g, self._b)
        self._hex = rgb_to_hex(self._r, self._g, self._b)
        self._notify(source)

    def update_from_hsv(self, h, s, v, source=None):
        h, s, v = int(round(h)), int(round(s)), int(round(v))

        self._h, self._s, self._v = h, s, v
        self._r, self._g, self._b = hsv_to_rgb(h, s, v)
        self._c, self._m, self._y, self._k = rgb_to_cmyk(self._r, self._g, self._b)
        self._hex = rgb_to_hex(self._r, self._g, self._b)
        self._notify(source)