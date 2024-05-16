from pytypes import typechecked
from typing import Optional, List, Union
import numpy as np

import pygame as pg

from constants import consts as c
from id_mapping import id_map, reverse_id_map
from images import img as i
from recipes import recipes
from ui.game_ui import ui
from structures.production.process_unit import ProcessUnit

class Factory(ProcessUnit):
    def __init__(self, row: int, col: int, direction: int):
        super().__init__(row, col)
        self.direction: int = direction
        self.recipe: Optional[str] = None
        self.storage: List[int] = []
        self.init_target()

    @typechecked
    def update(self, sm, im) -> None:
        if self.recipe is None:
            im.remove(self.row, self.col)

        if im.grid[self.row][self.col] != 0:
            item_inside = im.grid[self.row][self.col]
            if self.will_accept_item(item_inside.item):
                self.storage.append(item_inside.item)
            im.remove(self.row, self.col)

        if self.recipe_fulfilled():
            self.progress += c.dt

            if self.progress > recipes[self.recipe]["time"]:
                if not self.is_buffer_full():
                    self.progress = 0
                    self.manage_buffer(recipes[self.recipe]["output"])
                    self.storage = []

        if len(self.buffer) > 0:
            if im.grid[self.target_row][self.target_col] == 0 and sm.item_can_be_placed(self.target_row, self.target_col):
                im.add(self.target_row, self.target_col, self.buffer.pop(0))

    @typechecked
    def render(self) -> None:
        c.screen.blit(i.images[id_map["factory"]], (self.x - c.player_x, self.y - c.player_y))

        if self.recipe is not None:
            if self.progress != 0 and self.progress < recipes[self.recipe]["time"]:
                pg.draw.rect(c.screen, c.working_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 2)
            elif self.is_buffer_full():
                pg.draw.rect(c.screen, c.full_color, (self.x - c.player_x, self.y - c.player_y, c.cell_length, c.cell_length), 3)
        else:
            pg.draw.circle(c.screen, c.error_color, (self.x - c.player_x + c.cell_length // 2, self.y - c.player_y + c.cell_length // 2), 4 * c.cell_length // 5, 2)

    @typechecked
    def render_tooltip(self) -> None:
        pg.draw.rect(c.screen, c.target_color, (self.target_col * c.cell_length - c.player_x, self.target_row * c.cell_length - c.player_y, c.cell_length, c.cell_length), 3)

        if self.recipe is None:
            status = "NO RECIPE"
            ui.render_text(f"Factory [{status}]: (L/R) to rotate, (LMB) to select recipe")
        else:
            if self.is_buffer_full():
                status = "FULL"
            elif self.progress == 0:
                status = "WAITING"
            elif self.progress < recipes[self.recipe]["time"]:
                status = "WORKING"
            else:
                status = "ERROR"

            producing_item = recipes[self.recipe]["name"]
            ui.render_text(f"Factory [{status}]: Producing {producing_item} (L/R) to rotate, (LMB) to select recipe")

        self.render_recipe()

        if len(self.buffer) > 0:
            item_text = f"{len(self.buffer)} {reverse_id_map[self.buffer[0]].replace('_', ' ')}(s) in buffer"
            ui.render_desc(item_text)

    @typechecked
    def render_recipe(self) -> None:
        if self.recipe is not None:
            rel_x = self.x - c.player_x + (c.cell_length - self.recipe_text.get_width()) // 2

            if self.direction == 0:
                rel_y = self.y - c.player_y + 1.5 * c.cell_length
            else:
                rel_y = self.y - c.player_y - c.cell_length
            pg.draw.rect(c.screen, pg.Color("black"), (rel_x - 5, rel_y - 5, self.recipe_text.get_width() + 10, self.recipe_text.get_height() + 10))
            c.screen.blit(self.recipe_text, (rel_x, rel_y))

    @typechecked
    def set_recipe(self, recipe: Optional[Union[int, np.int64]]) -> None:
        #print("Setting recipe: ", recipe)
        #print("Current recipe: ", self.recipe)
        #print("Recipe is Type: ", type(recipe))

        if self.recipe is None or recipe is not None:
            self.recipe = recipe
            self.compose_recipe_text()
            self.storage = []
            self.clear_progress()

    @typechecked
    def compose_recipe_text(self) -> None:
        if self.recipe is not None:
            text = f"{recipes[self.recipe]['name']} requires "
            for item in recipes[self.recipe]["inputs"]:
                text += f"{reverse_id_map[item].replace('_', ' ')} ({recipes[self.recipe]['inputs'][item]}) "
            self.recipe_text = c.merriweather.render(text, True, pg.Color("white"))

    @typechecked
    def will_accept_item(self, item: Union[int, np.int64]) -> bool:
        if self.recipe is None:
            return False

        if self.is_buffer_full():
            return False

        if item in recipes[self.recipe]["inputs"]:
            num_in_storage = self.storage.count(item)
            if num_in_storage < recipes[self.recipe]["inputs"][item]:
                return True
            else:
                return False
        else:
            return False

    @typechecked
    def recipe_fulfilled(self) -> bool:
        if self.recipe is None:
            return False

        for item in recipes[self.recipe]["inputs"]:
            num_in_storage = self.storage.count(item)
            if num_in_storage < recipes[self.recipe]["inputs"][item]:
                return False

        return True

    @typechecked
    def rotate(self, direction: int) -> None:
        super().rotate(direction)

