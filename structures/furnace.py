from pytypes import typechecked
from typing import Optional, List

import pygame as pg

from constants import consts as c
from id_mapping import id_map, reverse_id_map
from images import img as i
from ui.game_ui import ui

#from items import item_manager as im
#from structures.structure import StructureManager as sm

class Furnace:
    def __init__(self, row: int, col: int, direction: int):
        self.row: int = row
        self.col: int = col
        self.direction: int = direction
        self.x: int = 0  # Position initialized in calc_position
        self.y: int = 0  # Position initialized in calc_position
        self.target_row: int = 0  # Position initialized in init_target
        self.target_col: int = 0  # Position initialized in init_target
        self.calc_position()
        self.init_target()

        self.smelting = None    # I don't know what type this is
        self.buffer: List[int] = []    # I don't know what type this is
        self.progress: int = 0   # I don't know what type this is

    @typechecked
    def update(self, sm, im) -> None:
        """AI is creating summary for update

        Args:
            sm ([type]): Structure Manager
            im ([type]): Item Manager
        """
        if self.smelting is None:
            if im.contains_ore(self.row, self.col):
                self.smelting = im.grid[self.row][self.col]
                im.remove(self.row, self.col)
                self.progress = 0
        else: 
            if self.progress < c.smelt_time:
                self.progress += c.dt
            elif len(self.buffer) < c.buffer_size:
                if self.smelting.item == id_map["iron_ore"]:
                    smelted_item_index = id_map["iron"]
                elif self.smelting.item == id_map["copper_ore"]:
                    smelted_item_index = id_map["copper"]

                self.buffer.append(smelted_item_index)
                self.smelting = None
                self.progress = 0

        if len(self.buffer) > 0:
            if im.grid[self.target_row][self.target_col] == 0 and sm.item_can_be_placed(self.target_row, self.target_col):
                im.add(self.target_row, self.target_col, self.buffer.pop(0))

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["furnace"]], (self.x - c.player_x, self.y - c.player_y))
        if self.progress != 0 and self.progress < c.smelt_time:
            pg.draw.rect(c.screen, c.working_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 2)
        elif len(self.buffer) == c.buffer_size:
            pg.draw.rect(c.screen, c.full_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 3)

    @typechecked
    def render_tooltip(self) -> None:
        pg.draw.rect(c.screen, c.target_color, (self.target_col * c.cell_length - c.player_x, self.target_row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)

        if len(self.buffer) == c.buffer_size:
            status = "FULL"
        elif self.smelting is None:
            status = "EMPTY"
        elif self.progress < c.smelt_time:
            status = "WORKING"
        else:
            status = "ERROR"

        ui.render_text(f"Furnace [{status}]: (L/R) to rotate")

        if len(self.buffer) > 0:
            item_text = f"{len(self.buffer)} metals(s) in buffer"
            ui.render_desc(item_text)

    @typechecked
    def rotate(self, direction: int) -> None:
        self.direction = (self.direction + direction) % 4
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

    def will_accept_item(self, item) -> None:
        if "ore" in reverse_id_map[item] and len(self.buffer) < c.buffer_size:
            return True
        else:
            return False