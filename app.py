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
        self.canvas.delete('section', 'line', 'rect', 'selected')

    def bind_rect(self):  
        x0, y0 = None, None

        def start_draw(event):
            nonlocal x0, y0

            self.canvas.delete('rect')

            if (x0, y0) == (None, None):
                x0, y0 = event.x, event.y

                self.canvas.create_rectangle(
                    x0, y0, x0, y0,
                    outline='red',
                    width=2,
                    dash=5,
                    tag='rect'
                )
            else:
                finish_draw(event)

        def draw_rectangle(event):
            x, y = event.x, event.y   

            if (x0, y0) != (None, None):  
                self.canvas.coords('rect', x0, y0, x, y)

        def finish_draw(event):
            nonlocal x0, y0

            x, y = event.x, event.y  

            self.canvas.create_rectangle(
                x0, y0, x, y, 
                width=2,
                outline='black',
                fill='black',
                stipple='gray12',
                tag='rect'
            )  
            
            x0, y0 = None, None

            self.cut_off()
                 
        self.canvas.bind('<Button-1>', start_draw)
        self.canvas.bind('<Motion>', draw_rectangle)

    def unbind_rect(self):
        self.canvas.delete('rect', 'selected')
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<Motion>')

    def cut_off(self):
        self.canvas.delete('selected')

        sections = self.canvas.find_withtag('section')
        rect = self.canvas.find_withtag('rect')

        x_min, y_min, x_max, y_max = self.canvas.bbox(rect)

        def get_code(x, y):
            code = 0

            if x < x_min:
                code |= 1 
            elif x > x_max:
                code |= 2 
            if y < y_min:
                code |= 4 
            elif y > y_max:
                code |= 8

            return code

        for section in sections:
            x1, y1, x2, y2 = self.canvas.coords(section)
            
            code1 = get_code(x1, y1)
            code2 = get_code(x2, y2)
            accept = False

            while True: 
        
                # If both endpoints lie within rectangle 
                if code1 == 0 and code2 == 0: 
                    accept = True
                    break
        
                # If both endpoints are outside rectangle 
                elif (code1 & code2) != 0: 
                    break
        
                # Some segment lies within the rectangle 
                else: 
        
                    # Line Needs clipping 
                    # At least one of the points is outside,  
                    # select it 
                    x = 1.0
                    y = 1.0
                    if code1 != 0: 
                        code_out = code1 
                    else: 
                        code_out = code2 
        
                    # Find intersection point 
                    # using formulas y = y1 + slope * (x - x1),  
                    # x = x1 + (1 / slope) * (y - y1) 
                    if code_out & 8: 
                        
                        # point is above the clip rectangle 
                        x = x1 + ((x2 - x1) / (y2 - y1)) * (y_max - y1) 
                        y = y_max 
        
                    elif code_out & 4: 
                        
                        # point is below the clip rectangle 
                        x = x1 + ((x2 - x1) / (y2 - y1)) * (y_min - y1) 
                        y = y_min 
        
                    elif code_out & 2: 
                        
                        # point is to the right of the clip rectangle 
                        y = y1 + ((y2 - y1) / (x2 - x1)) * (x_max - x1) 
                        x = x_max 
        
                    elif code_out & 1: 
                        
                        # point is to the left of the clip rectangle 
                        y = y1 + ((y2 - y1) / (x2 - x1)) * (x_min - x1)  
                        x = x_min 
        
                    # Now intersection point x, y is found 
                    # We replace point outside clipping rectangle 
                    # by intersection point 
                    if code_out == code1: 
                        x1 = x 
                        y1 = y 
                        code1 = get_code(x1, y1) 
        
                    else: 
                        x2 = x 
                        y2 = y 
                        code2 = get_code(x2, y2) 
                    
            if accept: 
                self.canvas.create_line(
                    x1, y1,
                    x2, y2,
                    fill='red',
                    width=3,
                    tag='selected'
                )
                    
                
