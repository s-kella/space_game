import os.path
import random
import time
import curses
import asyncio
from itertools import cycle

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(False)

    max_x, max_y = canvas.getmaxyx()
    x_mid = max_x // 2
    y_mid = max_y // 2
    coroutines = [fire(canvas, x_mid, y_mid),
                  animate_spaceship(canvas, x_mid, 1)]

    for _ in range(10):
        symbol = random.choice('+*.:')
        x = random.randint(0, max_x - 1)
        y = random.randint(0, max_y - 1)
        offset_tics = random.randint(0, 20)
        coroutines.append(blink(canvas, x, y, offset_tics, symbol))
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_direction_rocket(canvas, row, column, size_rows, size_columns, max_x, max_y):
    rows_direction, columns_direction, _ = read_controls(canvas)
    if row + rows_direction > 0 and row + rows_direction + size_rows < max_x:
        row += rows_direction
    if column + columns_direction > 0 and column + columns_direction + size_columns < max_y:
        column += columns_direction
    return row, column


async def animate_spaceship(canvas, column, row):
    rocket_1 = read_file('rocket_frame_1.txt')
    rocket_2 = read_file('rocket_frame_2.txt')
    max_x, max_y = canvas.getmaxyx()
    size_rows, size_columns = get_frame_size(rocket_1)
    frames = [rocket_1, rocket_1, rocket_2, rocket_2]
    for rocket in cycle(frames):
        row, column = get_direction_rocket(canvas, row, column, size_rows, size_columns, max_x, max_y)
        draw_frame(canvas, row, column, rocket)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, rocket, negative=True)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def read_file(file_name):
    file_path = os.path.join('animations', file_name)
    with open(file_path, 'r') as file:
        animation = file.read()
    return animation


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        for _ in range(offset_tics):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

