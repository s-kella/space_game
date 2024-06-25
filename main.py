import os.path
import random
import time
import curses
import asyncio


def draw(canvas):
    max_x, max_y = canvas.getmaxyx()
    canvas.nodelay(True)
    curses.curs_set(False)
    x_mid = max_x // 2
    y_mid = max_y // 2
    coroutines = [fire(canvas, x_mid, y_mid),
                  animate_spaceship(canvas, x_mid, 1)]

    for _ in range(10):
        symbol = random.choice('+*.:')
        x = random.randint(0, max_x - 1)
        y = random.randint(0, max_y - 1)
        coroutines.append(blink(canvas, x, y, symbol))
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)


async def animate_spaceship(canvas, column, row):
    rocket_1 = read_file('rocket_frame_1.txt')
    rocket_2 = read_file('rocket_frame_2.txt')
    while True:
        draw_frame(canvas, row, column, rocket_1)
        canvas.refresh()
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, rocket_1, negative=True)
        draw_frame(canvas, row, column, rocket_2)
        canvas.refresh()
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, rocket_2, negative=True)


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


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        for _ in range(random.randint(0, 20)):
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

