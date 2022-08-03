from .Util import COLOURS, TILESIZE
class Tile:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.colour = None

    def get_x(self):
        return self.x

    def set_x(self, x):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.colour = colour
