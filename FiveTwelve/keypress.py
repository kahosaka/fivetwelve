"""
Key press. For view Component. 

"""

LEFT = "Left"
RIGHT = "Right"
UP = "Up"
DOWN = "Down"
UNMAPPED = "Unmapped"

KEY_BINDINGS = {  # Arrow keys interpreted by Tk and graphics.py
    "Left": LEFT, "Right": RIGHT, "Up": UP, "Down": DOWN,
    # Left hand movement:
    "a": LEFT, "w": UP, "s": RIGHT, "z": DOWN,
    # VI / Vim editor movement:
    "h": LEFT, "j": DOWN, "k": UP, "l": RIGHT,
    # Numeric keypad movement:
    "4": LEFT, "6": RIGHT, "8": UP, "2": DOWN
}


class Command(object):
    """
    Interpret inputs from keyboard as set LEFT,
    RIGHT, UP, DOWN, UNMAPPED.
    """

    def __init__(self, game_view):
        self.game_view = game_view

    def next(self):
        key = self.game_view.get_key()
        if key not in KEY_BINDINGS:
            return UNMAPPED
        else:
            return KEY_BINDINGS[key]
