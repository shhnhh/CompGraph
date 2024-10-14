from tkinter import *
from tkinter import ttk
from scipy import interpolate
import numpy as np
import bisect

from canvas import CustomCanvas
from axes import AxesXY

class App(Tk):

    def __init__(self):
        super().__init__()

        self.width = 1000
        self.height = 800
        self.id_curve = None
        self.id_spline = None
        self.bc_type = StringVar(self, value='natural')
        self.tool = StringVar(self)
        self.prev = None

        self.tool.trace_add('write', self.set_tool)

        self.geometry(f'{self.width}x{self.height}')
        ttk.Style().theme_use('clam')

        self.grid_rowconfigure(1, weight=1)
        for i in range(4): self.grid_columnconfigure(i, weight=1)

        ttk.Radiobutton(
            self, 
            text='Нарисовать',
            variable=self.tool,
            value='draw',
            style='Toolbutton'
        ).grid(row=0, column=0)

        self.combobox = ttk.Combobox(
            self,
            values=('Жесткие', 'Мягкие', 'Циклические', 'Ациклические'),
            state='readonly')
        self.combobox.grid(row=0, column=1)

        ttk.Button(
            self, 
            text='Очистить',
            style='Toolbutton',
            command=self.clear
        ).grid(row=0, column=2)

        ttk.Radiobutton(
            self, 
            text='Редактироавние',
            variable=self.tool,
            value='edit',
            style='Toolbutton'
        ).grid(row=0, column=3)

        self.canvas = CustomCanvas(self, bg='white')
        self.canvas.grid(row=1, column=0, columnspan=5, sticky=NSEW)

        self.axes = AxesXY(self.canvas)

        self.canvas.bind('<Configure>', self.redraw)
        self.combobox.bind("<<ComboboxSelected>>", self.set_bc_type)

        self.combobox.set('Жесткие')

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
            case 'edit':
                self.unbind_edit()
            
        match self.tool.get():
            case 'draw':
                self.bind_draw()
            case 'edit':
                self.bind_edit()

        self.prev = self.tool.get()

    def set_bc_type(self, event):
        selection = self.combobox.get()

        match selection:
            case 'Жесткие':
                self.bc_type.set('natural')
            case 'Мягкие':
                self.bc_type.set('clamped')
            case 'Циклические':
                self.bc_type.set('periodic')
            case 'Ациклические':
                self.bc_type.set('not-a-knot')

        if self.id_curve is not None:
            coords = self.canvas.coords(self.id_curve)
            coords = np.reshape(coords, (len(coords) // 2, 2))

            self.draw_spline(coords)

    def draw_spline(self, coords):
        X, Y = map(list, zip(*coords))
        l, r = min(X), max(X)

        if len(X) > 2:
            if self.bc_type.get() == 'periodic':
                X.append(2 * X[-1] - X[-2])
                Y.append(Y[0])

            sp = interpolate.CubicSpline(X, Y, bc_type=self.bc_type.get())

            section = np.linspace(l, r, 200)
            values = sp(section)

            spline_coords = np.vstack([section, values]).T

            self.canvas.coords(self.id_spline, *np.concatenate(spline_coords))

    def bind_draw(self):
        if self.id_curve is None:
            coords = None
        else:
            coords = self.canvas.coords(self.id_curve)
            coords = list(map(list, zip(coords[::2], coords[1::2])))

        def put_point(event):
            nonlocal coords

            x, y = event.x, event.y

            if self.id_curve is None:
                coords = [[x, y]]

                self.id_curve = self.canvas.create_line(
                    x, y, x, y,
                    fill='black',
                    dash=(7, 7), 
                    width=3,
                )

                self.id_spline = self.canvas.create_line(
                    x, y, x, y,
                    fill='red',
                    width=3,
                )

            i = bisect.bisect(coords, [x, y])

            if coords[i - 1][0] == x:
                coords[i - 1][1] = y
            else:
                coords.insert(i, [x, y])

            if len(coords) > 1:
                self.canvas.coords(self.id_curve, *np.concatenate(coords))

            self.draw_spline(coords)

            self.canvas.create_circle(
                x, y, radius=5,
                fill='#007FFF',
                tag='point',
                outline='black'
            )
        
        self.canvas.bind('<Button-1>', put_point)

    def unbind_draw(self):
        self.canvas.unbind('<Button-1>')

    def clear(self):
        self.canvas.delete(
            self.id_curve, 
            self.id_spline,
            'point'
        )
        self.id_curve = None
        self.id_spline = None

    def bind_edit(self):
        x0, y0 = [None] * 2
        point = None
        coords = self.canvas.coords(self.id_curve)
        coords = np.reshape(coords, (len(coords) // 2, 2))
        points = list(self.canvas.find_withtag('point'))
        points.sort(key=lambda id: self.canvas.center(id))

        def start_drag(event):
            nonlocal x0, y0, point

            x0, y0 = event.x, event.y
            point = self.canvas.find_withtag(CURRENT)[0]

        def drag(event):
            nonlocal x0, y0, coords

            dx, dy = event.x - x0, event.y - y0
            x0, y0 = event.x, event.y

            idx = points.index(point)

            if (idx + 1 < len(coords) and coords[idx, 0] + dx >= coords[idx + 1, 0] or
                idx > 0 and coords[idx, 0] + dx <= coords[idx - 1, 0]):
                return

            coords[idx] += (dx, dy)

            self.canvas.coords(self.id_curve, *np.concatenate(coords))
            self.canvas.move(point, dx, dy)

            self.draw_spline(coords)

        def focus(event):
            point = self.canvas.find_withtag(CURRENT)[0]   
            self.canvas.itemconfig(point, fill='#E7F3FF')

        def unfocus(event):
            point = self.canvas.find_withtag(CURRENT)[0]   
            self.canvas.itemconfig(point, fill='#007FFF')
        
        self.canvas.tag_bind('point', '<Button-1>', start_drag)
        self.canvas.tag_bind('point', '<B1-Motion>', drag)
        self.canvas.tag_bind('point', '<Enter>', focus)
        self.canvas.tag_bind('point', '<Leave>', unfocus)

    def unbind_edit(self):
        self.canvas.tag_unbind('point', '<Button-1>')
        self.canvas.tag_unbind('point', '<B1-Motion>')
        self.canvas.tag_unbind('point', '<Enter>')
        self.canvas.tag_unbind('point', '<Leave>')