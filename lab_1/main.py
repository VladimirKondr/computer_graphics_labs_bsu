from color_model import ColorModel
from ui.app import App
from PIL import Image

if __name__ == "__main__":
    color_model = ColorModel()
    app = App(color_model)
    app.mainloop()