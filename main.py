import asyncio
import curses
import time
import random
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:'
border_size = 1


async def blink(canvas, row, column, symbol='*', offset_tics=1):
    for _ in range(offset_tics):
        await asyncio.sleep(0)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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


async def animate_spaceship(canvas, row, column, frames):
    rows, columns = canvas.getmaxyx()

    for frame in cycle(frames):
        frame_size_y, frame_size_x = get_frame_size(frame)
        frame_center_x = round(frame_size_x / 2)

        draw_frame(canvas, row, column - frame_center_x, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column - frame_center_x, frame, negative=True)

        direction_y, direction_x, space_pressed = read_controls(canvas)

        row += direction_y
        column += direction_x

        row = min(rows - frame_size_y - border_size, row)
        column = min(columns - frame_size_x + border_size, column)
        row = max(row, border_size)
        column = max(column, frame_center_x + border_size)


def get_random_coordinate(coordinate):
    return random.randint(border_size, coordinate - border_size * 2)


def load_frame(path_to_file):
    with open(path_to_file, "r") as my_file:
        return my_file.read()


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    rows, columns = canvas.getmaxyx()
    stars_count = (rows * columns) // 25

    center_row = round(rows / 2)
    center_column = round(columns / 2)

    rocket_frame_1 = load_frame('./animation/rocket_frame_1.txt')
    rocket_frame_2 = load_frame('./animation/rocket_frame_2.txt')

    rocket_frames = [rocket_frame_1, rocket_frame_1, rocket_frame_2, rocket_frame_2]

    coroutine_rocket = animate_spaceship(canvas, center_row, center_column, rocket_frames)

    coroutines_stars = [
        blink(canvas, get_random_coordinate(rows), get_random_coordinate(columns),
              random.choice(STAR_SYMBOLS), random.randint(1, 30))
        for _ in range(stars_count)
    ]

    coroutine_fire = fire(canvas, center_row, center_column)

    coroutines = [
        *coroutines_stars,
        coroutine_fire,
        coroutine_rocket
    ]

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except RuntimeError:
                coroutines.remove(coroutine)
                canvas.border()
            except StopIteration:
                break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)