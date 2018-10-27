"""
    This is the overall controller for this game.
    MVC is implemented.
    (Run this file to view the game).
"""
import model
import view
import keypress


def main():
    # Model component
    grid = model.Grid()
    # View component
    game_view = view.GameView(600, 600)
    grid_view = view.GridView(game_view, len(grid.tiles))
    grid.add_listener(grid_view)
    # Control component responsibility:
    commands = keypress.Command(game_view)
    grid.place_tile()

    # Continue the game until it is not empty.
    while grid.find_empty():
        grid.place_tile()
        cmd = commands.next()
        if cmd == keypress.LEFT:
            grid.left()
        elif cmd == keypress.RIGHT:
            grid.right()
        elif cmd == keypress.UP:
            grid.up()
        elif cmd == keypress.DOWN:
            grid.down()
        else:
            assert cmd == keypress.UNMAPPED

    game_view.lose(grid.score())


if __name__ == "__main__":
    main()
