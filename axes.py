from tkinter import *
from canvas import CustomCanvas

class AxesXY:

    def __init__(self, canvas : CustomCanvas): 
        self.canvas = canvas
        self.arrow_Y = None
        self.arrow_X = None

    def update(self):
        self.canvas.delete_arrow(self.arrow_Y)
        self.canvas.delete_arrow(self.arrow_X)

        self.canvas.update_idletasks()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.arrow_Y = self.canvas.create_arrow(
            50, height,
            50, 20,
            fill='black'
        )

        self.arrow_X = self.canvas.create_arrow(
            0, height - 50,
            width - 20, height - 50,
            fill='black'
        )

        self.canvas.create_markup(self.arrow_Y, 50, -1)
        self.canvas.create_markup(self.arrow_X, 50, 1)


        