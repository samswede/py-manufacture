from pytypes import typechecked
from typing import Optional, List

import pygame as pg

from constants import consts as c
from id_mapping import id_map, reverse_id_map
from images import img as i
from ui.game_ui import ui

from structures.production.process_unit import ProcessUnit

class Furnace(ProcessUnit):
    def __init__(self, row: int, col: int, direction: int):
        super().__init__(row, col)
        self.direction: int = direction
        self.smelting = None  # Type is unknown
        self.init_target()

    @typechecked
    def update(self, sm, im) -> None:
        if self.smelting is None:
            if im.contains_ore(self.row, self.col):
                self.smelting = im.grid[self.row][self.col]
                im.remove(self.row, self.col)
                self.clear_progress()
        else:
            if self.progress < c.smelt_time:
                self.progress += c.dt
            elif not self.is_buffer_full():
                smelted_item_index = self.get_smelted_item_index()
                if smelted_item_index is not None:
                    self.manage_buffer(smelted_item_index)
                    self.smelting = None
                    self.clear_progress()

        if len(self.buffer) > 0:
            if im.grid[self.target_row][self.target_col] == 0 and sm.item_can_be_placed(self.target_row, self.target_col):
                im.add(self.target_row, self.target_col, self.buffer.pop(0))

    def get_smelted_item_index(self) -> Optional[int]:
        if self.smelting.item == id_map["iron_ore"]:
            return id_map["iron"]
        elif self.smelting.item == id_map["copper_ore"]:
            return id_map["copper"]
        return None

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["furnace"]], (self.x - c.player_x, self.y - c.player_y))
        if self.progress != 0 and self.progress < c.smelt_time:
            pg.draw.rect(c.screen, c.working_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 2)
        elif self.is_buffer_full():
            pg.draw.rect(c.screen, c.full_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 3)

    @typechecked
    def render_tooltip(self) -> None:
        pg.draw.rect(c.screen, c.target_color, (self.target_col * c.cell_length - c.player_x, self.target_row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)

        if self.is_buffer_full():
            status = "FULL"
        elif self.smelting is None:
            status = "EMPTY"
        elif self.progress < c.smelt_time:
            status = "WORKING"
        else:
            status = "ERROR"

        ui.render_text(f"Furnace [{status}]: (L/R) to rotate")

        if len(self.buffer) > 0:
            item_text = f"{len(self.buffer)} metal(s) in buffer"
            ui.render_desc(item_text)

    @typechecked
    def rotate(self, direction: int) -> None:
        super().rotate(direction)

    @typechecked
    def will_accept_item(self, item) -> bool:
        if "ore" in reverse_id_map[item] and not self.is_buffer_full():
            return True
        return False
