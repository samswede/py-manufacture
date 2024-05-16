from typing import List, Tuple, Optional
from pytypes import typechecked

import pygame as pg
from constants import consts as c
from id_mapping import id_map
from images import img as i
from ui.game_ui import ui
from structures.distribution.distributor import Distributor

class Conveyor(Distributor):
    def __init__(self, row: int, col: int, direction: int):
        super().__init__(row, col, direction)
        self.init_squares()

    @typechecked
    def update(self, sm, im) -> None:
        pass

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["conveyor"]][self.direction], (self.x - c.player_x, self.y - c.player_y))

    @typechecked
    def render_tooltip(self) -> None:
        super().render_tooltip(c.source_color, c.target_color, "Conveyor [WORKING]: (L/R) to rotate")

    @typechecked
    def init_squares(self) -> None:
        if self.direction == 0:
            self.source_row = self.row + 1
            self.source_col = self.col
            self.target_row = self.row - 1
            self.target_col = self.col
        elif self.direction == 1:
            self.source_row = self.row
            self.source_col = self.col - 1
            self.target_row = self.row
            self.target_col = self.col + 1
        elif self.direction == 2:
            self.source_row = self.row - 1
            self.source_col = self.col
            self.target_row = self.row + 1
            self.target_col = self.col
        elif self.direction == 3:
            self.source_row = self.row
            self.source_col = self.col + 1
            self.target_row = self.row
            self.target_col = self.col - 1



class ConveyorUnderground(Distributor):
    def __init__(self, row: int, col: int, direction: int):
        self.source_row = row
        self.source_col = col
        self.length = c.ug_state
        super().__init__(row, col, direction)
        self.storage = []
        self.timers = []
        self.items_removed = []

    @typechecked
    def update(self, sm, im) -> None:
        for i in range(len(self.timers)):
            self.timers[i] += c.dt

        if len(self.storage) > 0 and self.timers[0] > self.moving_time:
            if im.grid[self.target_row][self.target_col] == 0 and sm.item_can_be_placed(self.target_row, self.target_col):
                im.add(self.target_row, self.target_col, self.storage.pop(0).item)
                self.timers.pop(0)

        if im.grid[self.source_row][self.source_col] != 0 and len(self.storage) < self.length:
            item = im.grid[self.source_row][self.source_col]
            self.storage.append(item)
            self.timers.append(0)
            im.remove(self.source_row, self.source_col)

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["conveyor_underground"]][self.direction], (self.source_x - c.player_x, self.source_y - c.player_y))
        c.screen.blit(i.images[id_map["conveyor_underground"]][self.direction + 4], (self.target_x - c.player_x, self.target_y - c.player_y))

    @typechecked
    def render_tooltip(self) -> None:
        pg.draw.line(
            c.screen, c.action_color, 
            (self.source_x - c.player_x + c.cell_length // 2, self.source_y - c.player_y + c.cell_length // 2), 
            (self.target_x - c.player_x + c.cell_length // 2, self.target_y - c.player_y + c.cell_length // 2), 
            3
        )
        status = "FULL" if len(self.storage) == self.length else "EMPTY" if len(self.storage) == 0 else "WORKING"
        ui.render_text(f"Underground Conveyor [{status}]")

    @typechecked
    def init_target(self) -> None:
        self.target_row = self.source_row
        self.target_col = self.source_col

        if self.direction == 0:
            self.target_row -= self.length
        elif self.direction == 1:
            self.target_col += self.length
        elif self.direction == 2:
            self.target_row += self.length
        elif self.direction == 3:
            self.target_col -= self.length

    @typechecked
    def calc_position(self) -> None:
        self.source_x = self.source_col * c.cell_length
        self.source_y = self.source_row * c.cell_length
        self.target_x = self.target_col * c.cell_length
        self.target_y = self.target_row * c.cell_length
        self.moving_time = self.length * c.cell_length / c.conveyor_speed

    @typechecked
    def can_accept_item(self, row: int, col: int) -> bool:
        if row != self.source_row or col != self.source_col:
            return True
        return len(self.storage) < self.length