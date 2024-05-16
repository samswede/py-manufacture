from typing import List, Tuple, Optional
from pytypes import typechecked
from abc import ABC

from constants import consts as c

import pygame as pg
from ui.game_ui import ui

from structures.shared import Structure

class Distributor(Structure, ABC):
    def __init__(self, row: int, col: int, direction: int) -> None:
        super().__init__(row, col)
        self.direction: int = direction
        self.init_target()
    
    @typechecked
    def rotate(self, rotation: int) -> None:
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

    @typechecked
    def calc_position(self) -> None:
        self.x = self.col * c.cell_length
        self.y = self.row * c.cell_length

    @typechecked
    def render_tooltip(self, source_color, target_color, status_text: str) -> None:
        pg.draw.rect(c.screen, source_color, (self.col * c.cell_length - c.player_x, self.row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)
        pg.draw.rect(c.screen, target_color, (self.target_col * c.cell_length - c.player_x, self.target_row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)
        ui.render_text(status_text)

    @staticmethod
    @typechecked
    def can_be_directed_to(sm, im, row, col) -> bool:
        return im.grid[row][col] == 0 and sm.item_can_be_placed(row, col)
