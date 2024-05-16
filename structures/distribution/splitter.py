from typing import List, Tuple, Optional
from pytypes import typechecked

import pygame as pg
from constants import consts as c
from id_mapping import id_map
from images import img as i
from ui.game_ui import ui
from structures.distribution.distributor import Distributor

class Splitter(Distributor):
    def __init__(self, row: int, col: int, direction: int):
        super().__init__(row, col, direction)
        self.state = 1
        self.item = None
        self.target1_open = False
        self.target2_open = False
        self.init_targets()

    @typechecked
    def update(self, sm, im) -> None:
        self.target1_open = self.can_be_directed_to(sm, im, self.target1_row, self.target1_col)
        self.target2_open = self.can_be_directed_to(sm, im, self.target2_row, self.target2_col)

        if im.grid[self.row][self.col] != 0:
            self.item = im.grid[self.row][self.col].item

            if self.state == 1:
                if self.target1_open:
                    self.direct_to_one(im)
                    self.state = 2
                elif self.target2_open:
                    self.direct_to_two(im)
                    self.state = 1
            elif self.state == 2:
                if self.target2_open:
                    self.direct_to_two(im)
                    self.state = 1
                elif self.target1_open:
                    self.direct_to_one(im)
                    self.state = 2

    @typechecked
    def direct_to_one(self, im) -> None:
        im.remove(self.row, self.col)
        im.add(self.target1_row, self.target1_col, self.item)

    @typechecked
    def direct_to_two(self, im) -> None:
        im.remove(self.row, self.col)
        im.add(self.target2_row, self.target2_col, self.item)

    @typechecked
    def can_accept_item(self, a: int, b: int) -> bool:
        return self.target1_open or self.target2_open

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["splitter"]][self.direction], (self.x - c.player_x, self.y - c.player_y))

    @typechecked
    def render_tooltip(self) -> None:
        status = "FULL" if not self.target1_open and not self.target2_open else "WORKING"
        super().render_tooltip(c.source_color, c.target_color, f"Splitter [{status}]: (L/R) to rotate")

    @typechecked
    def init_targets(self) -> None:
        if self.direction == 0:
            self.target1_row = self.target2_row = self.row - 1
            self.target1_col = self.col - 1
            self.target2_col = self.col + 1
        elif self.direction == 1:
            self.target1_col = self.target2_col = self.col + 1
            self.target1_row = self.row - 1
            self.target2_row = self.row + 1
        elif self.direction == 2:
            self.target1_row = self.target2_row = self.row + 1
            self.target1_col = self.col + 1
            self.target2_col = self.col - 1
        elif self.direction == 3:
            self.target1_col = self.target2_col = self.col - 1
            self.target1_row = self.row + 1
            self.target2_row = self.row - 1
