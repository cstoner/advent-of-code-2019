#!/usr/bin/env python3
import copy
from collections import defaultdict
from enum import IntEnum
from typing import Dict, Generator

from intcode import MachineState, IntCodeComputer, HaltException
from intcode.devices import InputDevice, OutputDevice


class PaintColor(IntEnum):
    BLACK = 0
    WHITE = 1

    def __str__(self):
        return {
            self.BLACK: '.',
            self.WHITE: '#'
        }[self.value]


class RobotDirection:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    to_vec = {
        UP: (0, 1),
        RIGHT: (1, 0),
        DOWN: (0, -1),
        LEFT: (-1, 0)
    }

    to_str = {
        UP: '^',
        RIGHT: '>',
        DOWN: 'v',
        LEFT: '<'
    }


class PainterRobot:
    def __init__(self, init_x=0, init_y=0, init_dir=RobotDirection.UP):
        self.x: int = init_x
        self.y: int = init_y
        self.dir: int = init_dir

    def turn_right(self):
        self.dir = (self.dir + 1) % 4

    def turn_left(self):
        self.dir = (self.dir + 3) % 4

    def go_forward(self):
        (x0, y0) = RobotDirection.to_vec[self.dir]
        self.x += x0
        self.y += y0

    def __str__(self):
        return RobotDirection.to_str[self.dir]


class SpaceShipGrid:
    def __init__(self):
        self.grid: Dict[(int, int), PaintColor] = defaultdict(lambda: PaintColor.BLACK)

    def get(self, x: int, y: int) -> PaintColor:
        return self.grid[(x, y)]

    def set(self, x: int, y: int, value: PaintColor) -> None:
        self.grid[(x, y)] = value

    def render_with_robot(self, robot: PainterRobot) -> str:
        grid_keys = self.grid.keys()
        if len(grid_keys) == 0:
            return str(robot)

        x_keys = [x for (x, _) in grid_keys] + [robot.x]
        y_keys = [y for (_, y) in grid_keys] + [robot.y]
        min_x = min(x_keys)
        max_x = max(x_keys)
        min_y = min(y_keys)
        max_y = max(y_keys)

        delta_x = abs(max_x - min_x) + 1
        delta_y = abs(max_y - min_y) + 1

        empty_row = [str(PaintColor.BLACK)] * delta_x
        full_grid = [copy.copy(empty_row) for _ in range(delta_y)]

        # "upper left" of grid is (min_x, max_y), so (0, 0) is actually at (0-min_x, max_y)
        origin_0x = 0 - min_x
        origin_0y = max_y

        for (x, y) in grid_keys:
            translated_x = origin_0x + x
            translated_y = origin_0y - y

            full_grid[translated_y][translated_x] = str(PaintColor(self.grid[(x, y)]))

        robot_x = origin_0x + robot.x
        robot_y = origin_0y - robot.y

        full_grid[robot_y][robot_x] = str(robot)
        joined_rows = ["".join(row) for row in full_grid]
        return "\n".join(joined_rows)


class GridAndRobot(InputDevice, OutputDevice):
    def __init__(self):
        self.grid = SpaceShipGrid()
        self.robot = PainterRobot()

    def io_get(self) -> Generator[PaintColor, None, None]:
        while True:
            get_val = self.grid.get(self.robot.x, self.robot.y)
            yield get_val

    def io_put(self) -> Generator[None, PaintColor, None]:
        while True:
            raw_paint_color = yield
            paint_color = PaintColor(raw_paint_color)
            self.grid.set(self.robot.x, self.robot.y, paint_color)
            raw_turn_dir = yield
            if raw_turn_dir == 0:
                self.robot.turn_left()
            elif raw_turn_dir == 1:
                self.robot.turn_right()
            else:
                raise Exception(f"Unknown direction: {raw_turn_dir}")
            self.robot.go_forward()

    def __str__(self):
        return self.grid.render_with_robot(self.robot)


with open('input.txt') as INPUT:
    day11_inputs = [int(i) for i in INPUT.read().split(',')]

grid_and_robot = GridAndRobot()
grid_and_robot.grid.set(0, 0, PaintColor.WHITE)
day11_machine_state = MachineState(day11_inputs, grid_and_robot, grid_and_robot)
day11_computer = IntCodeComputer(day11_machine_state)

try:
    day11_computer.exec_program()
except HaltException:
    print(grid_and_robot)
