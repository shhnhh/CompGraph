from tkinter import *
from tkinter import ttk
from random import randint
import numpy as np

from canvas import CustomCanvas
from axes import AxesXY

class App(Tk):

    def __init__(self):
        super().__init__()

        self.width = 1000
        self.height = 800
        self.tool = StringVar(self)
        self.prev = None

        self.tool.trace_add('write', self.set_tool)

        self.geometry(f'{self.width}x{self.height}')
        ttk.Style().theme_use('clam')

        toolbar = ttk.Frame(self)
        toolbar.pack(side=TOP, fill=X)

        ttk.Radiobutton(
            toolbar, 
            text='Нарисовать отрезок',
            variable=self.tool,
            value='draw',
            style='Toolbutton'
        ).pack(side=LEFT)

        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y)

        ttk.Button(
            toolbar, 
            text='Случайный отрезок',
            style='Toolbutton',
            command=self.rand
        ).pack(side=LEFT)

        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y)

        ttk.Button(
            toolbar, 
            text='Очистить',
            style='Toolbutton',
            command=self.clear
        ).pack(side=LEFT)

        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y)

        ttk.Radiobutton(
            toolbar, 
            text='Нарисовать рамку',
            variable=self.tool,
            value='rect',
            style='Toolbutton'
        ).pack(side=LEFT)

        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y)

        self.canvas = CustomCanvas(self, bg='white')
        self.canvas.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.axes = AxesXY(self.canvas)

        self.canvas.bind('<Configure>', self.redraw)

    def redraw(self, event):
        self.update_idletasks()
        self.axes.update()

        kx = self.winfo_width() / self.width
        ky = self.winfo_height() / self.height

        self.canvas.scale(ALL, 0, 0, kx, ky)

        self.width = self.winfo_width()
        self.height = self.winfo_height()

    def run(self):
        self.mainloop()

    def set_tool(self, *args):
        match self.prev:
            case 'draw':
                self.unbind_draw()
            case 'rect':
                self.unbind_rect()
            
        match self.tool.get():
            case 'draw':
                self.bind_draw()
            case 'rect':
                self.bind_rect()

        self.prev = self.tool.get()

    def bind_draw(self):
        x0, y0 = None, None

        def put_point(event):
            nonlocal x0, y0

            x, y = event.x, event.y

            if (x0, y0) == (None, None):
                x0, y0 = x, y
            else:
                self.canvas.delete('line')

                self.canvas.create_line(
                    x0, y0,
                    x, y,
                    fill='black',
                    width=2,
                    tag='section'
                )

                x0, y0 = None, None

        def draw_line(event):
            nonlocal x0, y0

            x, y = event.x, event.y

            if (x0, y0) != (None, None):
                self.canvas.delete('line')

                self.canvas.create_line(
                    x0, y0,
                    x, y,
                    fill='red',
                    width=2,
                    dash=5,
                    tag='line'
                )
        
        self.canvas.bind('<Button-1>', put_point)
        self.canvas.bind('<Motion>', draw_line)

    def unbind_draw(self):
        self.canvas.delete('line')
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<Motion>')

    def rand(self):
        x0, x = [randint(0, self.width) for _ in range(2)]
        y0, y = [randint(0, self.height) for _ in range(2)]

        self.canvas.create_line(
            x0, y0,
            x, y,
            fill='black',
            width=2,
            tag='section'
        )        

    def clear(self):
        self.canvas.delete('section')

    def bind_rect(self):  
        x0, y0 = None, None
        id_rect = None

        def start_draw(event):
            nonlocal x0, y0, id_rect

            self.canvas.delete('rect')

            if id_rect is not None:
                return

            x0, y0 = event.x, event.y

            id_rect = self.canvas.create_rectangle(
                x0, y0, x0, y0,
                outline='red',
                width=2,
                dash=5
            )

        def draw_rectangle(event):
            if id_rect is None:
                return
            
            x, y = event.x, event.y     

            self.canvas.coords(id_rect, x0, y0, x, y)

        def finish_draw(event):
            nonlocal x0, y0, id_rect

            x, y = event.x, event.y

            if id_rect is None or (x0, y0) == (x, y):
                return      

            self.canvas.create_rectangle(
                x0, y0, x, y, 
                width=2,
                outline='black',
                fill='black',
                stipple='gray12',
                tag='rect'
            )  

            self.canvas.delete(id_rect)   
            
            x0, y0 = None, None
            id_rect = None
                 
        self.canvas.bind('<Button-1>', start_draw)
        self.canvas.bind('<Motion>', draw_rectangle)
        self.canvas.bind('<ButtonRelease-1>', finish_draw)

    def unbind_rect(self):
        self.canvas.delete('rect')
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<ButtonRelease-1>')