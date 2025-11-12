import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.app import ImageProcessorApp


if __name__ == "__main__":
    app = ImageProcessorApp()
    app.mainloop()
