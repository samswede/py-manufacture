from abc import ABC, abstractmethod
from pytypes import typechecked
from typing import List, Optional, Union
import numpy as np

from structures.shared import Structure
from constants import consts as c

class ProcessUnit(Structure, ABC):
    def __init__(self, row: int, col: int):
        super().__init__(row, col)
        self.buffer: List[Optional[Union[int, np.int64]]] = []  
        self.progress: int = 0
        self.buffer_size: int = c.buffer_size  # Assuming there's a constant buffer size

    @typechecked
    @abstractmethod
    def update(self) -> None:
        """Process or move items if conditions are met, to be implemented specifically in each unit."""
        pass

    @typechecked
    @abstractmethod
    def render(self) -> None:
        """Render the specific unit, must be overridden in each subclass."""
        pass

    @typechecked
    def manage_buffer(self, item: Optional[Union[int, np.int64]]) -> None:
        """Manage buffer operations, adding or removing items."""
        if len(self.buffer) < self.buffer_size:
            self.buffer.append(item)
        # More complex logic can be implemented as needed

    @typechecked
    def is_buffer_full(self) -> bool:
        """Check if the buffer is full."""
        return len(self.buffer) >= self.buffer_size

    @typechecked
    def clear_progress(self) -> None:
        """Reset progress for the next cycle."""
        self.progress = 0
