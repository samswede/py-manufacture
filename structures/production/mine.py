from pytypes import typechecked
from typing import Optional

import pygame as pg

from constants import consts as c
from id_mapping import id_map, reverse_id_map
from images import img as i
from world import world as w
from ui.game_ui import ui
from structures.production.process_unit import ProcessUnit

class Mine(ProcessUnit):
    def __init__(self, row: int, col: int, direction: int):
        super().__init__(row, col)
        self.direction: int = direction
        self.mining: Optional[int] = None
        self.target_blocked: bool = False
        self.init_target()

    @typechecked
    def update(self, sm, im) -> None:
        if self.mining is None and not self.is_buffer_full():
            if w.grid[self.row][self.col] > 0:
                self.mining = w.grid[self.row][self.col]
                self.clear_progress()
        else:
            if self.progress < c.mine_time:
                self.progress += c.dt
            elif not self.is_buffer_full():
                self.manage_buffer(self.mining)
                self.mining = None
                self.clear_progress()

        if len(self.buffer) > 0:
            if im.grid[self.target_row][self.target_col] == 0 and sm.item_can_be_placed(self.target_row, self.target_col):
                im.add(self.target_row, self.target_col, self.buffer.pop(0))

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["mine"]], (self.x - c.player_x, self.y - c.player_y))

        if self.progress != 0 and self.progress < c.mine_time:
            pg.draw.rect(c.screen, c.working_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 2)
        elif self.is_buffer_full():
            pg.draw.rect(c.screen, c.full_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 3)

    @typechecked
    def render_tooltip(self) -> None:
        pg.draw.rect(c.screen, c.target_color, (self.target_col * c.cell_length - c.player_x, self.target_row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)

        if w.grid[self.row][self.col] == 0:
            status = "NO ORE"
        elif self.is_buffer_full():
            status = "FULL"
        elif self.progress < c.mine_time:
            status = "WORKING"
        else:
            status = "ERROR"

        ui.render_text(f"Mine [{status}]: (L/R) to rotate")

        if len(self.buffer) > 0:
            item_text = f"{len(self.buffer)} {reverse_id_map[self.buffer[0]].replace('_', ' ')}(s) in buffer"
            ui.render_desc(item_text)

    @typechecked
    def rotate(self, direction: int) -> None:
        super().rotate(direction)

