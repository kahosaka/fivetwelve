"""
    Game logic. Model Component. Produces event 
    notifications to trigger view updates.
    Implemented by Kiana Hosaka.
"""

import random
from enum import Enum
from typing import List, Tuple, Optional

GRID_SIZE = 4

# --- Interface for 'View' objects to connect and listen


class EventKind(Enum):
    """ Events to notify Listener. """
    tile_created = 1
    tile_updated = 2
    tile_removed = 3


class GameEvent(object):
    """ Event that may be depicted. """

    def __init__(self, kind: EventKind,  tile: "Tile"):
        self.kind = kind
        self.tile = tile

    def __repr__(self):
        return "GameEvent({}, {})".format(self.kind, self.tile)


class GameListener(object):
    """ 
        Abstract base class. Objects listen to game events
        in MVC. Listeners must implement 'notify' method.
    """

    def notify(self, event: GameEvent):
        raise NotImplementedError(
            "Game Listener classes must implement 'notify'")

# -------------------------------------------


class GameElement(object):
    """
        Base class for game elements. Supports depcition
        through MVC.
    """

    def __init__(self):
        """
            Game evenets can have 0 or more listeners 
            to react to notifications.
        """
        self._listeners = []

    def add_listener(self, listener: GameListener):
        self._listeners.append(listener)

    def notify_all(self, event: GameEvent):
        """
            Notify view components of significant events. View 
            will decide how to adjust graphics. Additional 
            information goes into 'data' parameter.
        """
        for listener in self._listeners:
            listener.notify(event)


class Grid(GameElement):
    """ The game grid. """

    def __init__(self):
        super().__init__()
        self.rows = GRID_SIZE
        self.cols = GRID_SIZE
        self.sum = 0
        self.tiles = []
        for row in range(self.rows):
            columns = []
            for col in range(self.cols):
                columns.append(None)
            self.tiles.append(columns)

    def __str__(self):
        """ String representation """
        rep = []
        for row in self.tiles:
            labels = [str(x) for x in row]
            rep.append("[{}]".format(",".join(labels)))
        return "[{}]".format(",".join(rep))

    def in_bounds(self, row: int, col: int) -> bool:
        """ In bounds if (row, col) are considered
            'valid' rows and columns of grid. 
         """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def as_list(self) -> List[List[int]]:
        """ Grid as list of lists of numbers. 
            Zero represents an empty tile.
        """
        rep = []
        for row in self.tiles:
            value_list = []
            for tile in row:
                if tile is None:
                    value_list.append(0)
                else:
                    value_list.append(tile.value)
            rep.append(value_list)
        return rep

    def set_tiles(self, rep: List[List[int]]):
        """ Set tiles to a saved configuration, which must
            have the correct dimensions (e.g., 4 rows of 4 columns
            if grid size is 4). Zero represents an empty tile.
        """
        self.tiles = []
        for row in range(self.rows):
            row_tiles = []
            for col in range(self.cols):
                if rep[row][col] == 0:
                    row_tiles.append(None)
                else:
                    val = rep[row][col]
                    tile = Tile(self, row, col, value=val)
                    row_tiles.append(tile)
                    self.notify_all(GameEvent(EventKind.tile_created, tile))
            self.tiles.append(row_tiles)

    def score(self) -> int:
        """ Score is total value of all tiles.
            Differs from 2048 scoring.
        """
        return self.sum

    # Game logic -------------------
    def find_empty(self) -> Optional[Tuple[int, int]]:
        """ Find an empty cell to drop new tile.
            Returns a row, col pair or None if
            no empty spots on grid.
        """
        candidates = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.tiles[row][col] is None:
                    pos = (row, col)
                    candidates.append(pos)
        if candidates == []:
            return None
        return random.choice(candidates)

    def place_tile(self):
        """ Place new tile randomly on the grid.
            New value is always 2 or 4 (10% of time).
        """
        spot = self.find_empty()
        assert spot is not None
        row, col = spot

        if random.randint(1, 10) == 4:
            tile = Tile(self, row, col, 4)
        else:
            tile = Tile(self, row, col, 2)

        self.tiles[row][col] = tile
        self.notify_all(GameEvent(EventKind.tile_created, tile))

    # Game moves -------------------
    def left(self):
        """ Slide tiles to the left. """
        movement_vector = [-1, 0]
        for row in self.tiles:
            for col in row:
                if col:
                    col.slide(movement_vector)

    def right(self):
        """ Slide tiles to the right. """
        movement_vector = [1, 0]
        for row in self.tiles:
            for col in reversed(row):
                if col:
                    col.slide(movement_vector)

    def up(self):
        """ Slide tiles up. """
        movement_vector = [0, -1]
        for row in self.tiles:
            for col in row:
                if col:
                    col.slide(movement_vector)

    def down(self):
        """ Slide tiles down. """
        movement_vector = [0, 1]
        for row in reversed(self.tiles):
            for col in row:
                if col:
                    col.slide(movement_vector)


class Tile(GameElement):
    """A slidy numbered thing."""

    def __init__(self, grid: Grid, row: int, col: int, value=2):
        super().__init__()
        self.grid = grid
        self.row = row
        self.col = col
        self.value = value

    def __repr__(self):
        return "Tile({}) at {},{}".format(self.value, self.row, self.col)

    def __str__(self):
        return str(self.value)

    def slide(self, movement_vector: Tuple[int, int]):
        """ Slide the tile in given direction
            Note we must update grid as well as
            tile.
        """
        dx, dy = movement_vector
        row, col = self.row, self.col
        while True:
            trial_x = row + dy
            trial_y = col + dx
            if not self.grid.in_bounds(trial_x, trial_y):
                # Edge of board
                break
            if not self.grid.tiles[trial_x][trial_y]:
                # Slide over empty space
                row, col = trial_x, trial_y
                self.move(self.grid, row, col)
            elif self.grid.tiles[trial_x][trial_y].value == self.value:
                # Matching tile, merge and continue
                row, col = trial_x, trial_y
                self.merge(self.grid.tiles[trial_x][trial_y])
                self.move(self.grid, row, col)
                self.grid.sum += self.value
                print(self.grid.sum)
            else:
                # Reached tile with a different value
                break

    def move(self, grid, row, col):
        """ Update position. """
        self.grid.tiles[self.row][self.col] = None
        self.row = row
        self.col = col
        self.grid.tiles[row][col] = self
        self.notify_all(GameEvent(EventKind.tile_updated, self))

    def merge(self, other):
        """ This tile absorbs other tile. """
        self.value = self.value + other.value
        other.remove()
        self.notify_all(GameEvent(EventKind.tile_updated, self))

    def remove(self):
        self.notify_all(GameEvent(EventKind.tile_removed, self))
