from asyncio.windows_events import NULL
from curses.ascii import NUL


class Board:
    def __init__(self):
        self.height = 0
        self.width = 0
        self.timer = 0

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getTime(self):
        return self.timer
