from typing import Tuple
from constants import consts as c
from pytypes import typechecked
from abc import ABC, abstractmethod

class Structure(ABC):
    def __init__(self, row: int, col: int) -> None:
        self.row: int = row
        self.col: int = col
        self.x: int = 0
        self.y: int = 0
        self.calc_position()

    @typechecked
    def calc_position(self) -> None:
        """ Calculate the screen (x, y) position from the grid (row, col) position. """
        self.x = self.col * c.cell_length
        self.y = self.row * c.cell_length

    @typechecked
    @abstractmethod
    def render(self) -> None:
        """ Render the structure at its current position. """
        pass

    @typechecked
    def get_position(self) -> Tuple[int, int]:
        """ Return the grid position as a tuple. """
        return (self.row, self.col)
    
    @typechecked
    def rotate(self, rotation: int) -> None:
        """ Rotate the structure by the given amount. """
        self.direction = (self.direction + rotation) % 4
        self.init_target()

    @typechecked
    def init_target(self) -> None:
        if self.direction == 0:
            self.target_row = self.row - 1
            self.target_col = self.col
        elif self.direction == 1:
            self.target_row = self.row
            self.target_col = self.col + 1
        elif self.direction == 2:
            self.target_row = self.row + 1
            self.target_col = self.col
        elif self.direction == 3:
            self.target_row = self.row
            self.target_col = self.col - 1
