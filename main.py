import asyncio
import curses
import time
import random
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:'


async def blink(canvas, row, column, symbol='*'):
    for _ in range(random.randint(1, 30)):
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


async def animate_spaceship(canvas, frames):
    row, column = canvas.getmaxyx()
    start_x = column // 2
    start_y = row // 2

    frame_size_y, frame_size_x = get_frame_size(frames[0])
    frame_pos_x = start_x
    frame_pos_y = start_y

    border_size = 1

    for item in cycle(frames):

        direction_y, direction_x, space_pressed = read_controls(canvas)

        frame_pos_x += direction_x
        frame_pos_y += direction_y

        frame_x_max = frame_pos_x + frame_size_x
        frame_y_max = frame_pos_y + frame_size_y

        field_x_max = column - border_size
        field_y_max = row - border_size

        frame_pos_x = min(frame_x_max, field_x_max) - frame_size_x
        frame_pos_y = min(frame_y_max, field_y_max) - frame_size_y
        frame_pos_x = max(frame_pos_x, border_size)
        frame_pos_y = max(frame_pos_y, border_size)

        draw_frame(canvas, frame_pos_y, frame_pos_x, item)
        canvas.refresh()

        for _ in range(3):
            await asyncio.sleep(0)

        draw_frame(canvas, frame_pos_y, frame_pos_x, item, negative=True)


def get_coordinate(coordinate):
    return random.randint(1, coordinate - 2)


def load_frame(path_to_file):
    with open(path_to_file, "r") as my_file:
        return my_file.read()


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    row, column = canvas.getmaxyx()
    star_count = (row * column) // 25

    rocket_frame_1 = load_frame('./animation/rocket_frame_1.txt')
    rocket_frame_2 = load_frame('./animation/rocket_frame_2.txt')

    rocket_frames = [rocket_frame_1, rocket_frame_2]

    coroutine_rocket = animate_spaceship(canvas, rocket_frames)

    coroutines_stars = [blink(canvas, get_coordinate(row), get_coordinate(column),
                              random.choice(STAR_SYMBOLS)) for i in range(star_count)]

    coroutine_fire = fire(canvas, row // 2, column // 2)

    coroutines = []
    coroutines += coroutines_stars
    coroutines.append(coroutine_fire)

    while True:
        coroutine_rocket.send(None)
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except RuntimeError:
                coroutines.remove(coroutine)
                canvas.border()
            except StopIteration:
                break
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
