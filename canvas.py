from tkinter import *
import numpy as np

class CustomCanvas(Canvas):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def create_arrow(self, x1, y1, x2, y2, **kwargs):

        id = self.create_line(x1, y1, x2, y2, **kwargs)
        self.addtag(f'arrow{id}', 'withtag', id)

        v = np.array([x2 - x1, y2 - y1])
        e = v / np.linalg.norm(v)
        v = np.array([x2, y2]) - e * 20

        left_line = self.create_line(*v, x2, y2, tag=f'arrow{id}', **kwargs)
        self.rotate(left_line, (x2, y2), np.pi / 6)

        right_line = self.create_line(*v, x2, y2, tag=f'arrow{id}', **kwargs)
        self.rotate(right_line, (x2, y2), -np.pi / 6)

        return id
    
    def delete_arrow(self, id):
        self.delete(f'arrow{id}')
        self.delete(f'markup{id}')        
    
    def center(self, tagOrId):
        coords = self.coords(tagOrId)

        centroid_x = np.mean(coords[::2])
        centroid_y = np.mean(coords[1::2])

        return centroid_x, centroid_y

    def rotate(self, tagOrId, origin, angle):

        origin = np.array(origin)

        rot_matrix = np.array([[np.cos(angle), np.sin(angle)], 
                               [-np.sin(angle),  np.cos(angle)]])

        for id in self.find_withtag(tagOrId):
            coords = np.array(self.coords(id))
            coords = np.reshape(coords, (len(coords) // 2, 2))
            coords -= origin
            
            new_coords = np.dot(coords, rot_matrix)
            new_coords += origin
            new_coords = np.reshape(new_coords, (len(new_coords) * 2,))

            self.coords(id, *new_coords)

    def create_markup(self, id_arrow, interval, place):
        x1, y1, x2, y2 = self.coords(id_arrow)
        center = self.center(id_arrow)

        v = np.array([x2 - x1, y2 - y1])
        e = v / np.linalg.norm(v)

        length = int(np.linalg.norm(v))
        n = length // interval

        zero = np.array([x1, y1]) + e * 50

        for i in range(1, n - 1):
            point = zero + e * i * interval

            line = self.create_line(
                *point, *(point + 5 * e), 
                fill='red',
                tag=f'markup{id_arrow}'
            )
            
            self.rotate(line, point, np.pi / 2 * place)
            
            x1, y1, x2, y2 = self.coords(line)
            v = np.array([x2 - x1, y2 - y1])

            self.create_text(
                *(point + v * 3), 
                text=f'{i}',
                tag=f'markup{id_arrow}'
            )
    
    def create_circle(self, x, y, radius, **kwargs):
        sides = 15

        coords = np.array([ 
            ((np.cos(th)) * radius + x, 
             (np.sin(th)) * radius + y) 
            for th in [i * (2 * np.pi) / sides for i in range(sides)] 
        ])
        coords = np.concatenate(coords)

        return self.create_polygon(*coords, **kwargs)

        



