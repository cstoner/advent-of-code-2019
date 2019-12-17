#!/usr/bin/env python3
import copy
import os
from collections import defaultdict
from enum import IntEnum
from typing import Dict, Generator

from intcode import MachineState, IntCodeComputer, HaltException
from intcode.devices import InputDevice, OutputDevice


class ScreenTile(IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    H_PADDLE = 3
    BALL = 4

    def __str__(self):
        return {
            self.EMPTY: ' ',
            self.WALL: '#',
            self.BLOCK: 'X',
            self.H_PADDLE: '-',
            self.BALL: '@'
        }[self.value]


class JoyStick(InputDevice):
    LEFT = -1
    NEUT = 0
    RIGHT = 1

    def __init__(self, pos=NEUT):
        self.pos = pos

    def io_get(self) -> Generator[int, None, None]:
        while True:
            yield self.pos

    def set_pos(self, pos):
        self.pos = pos


class OutputScreen(OutputDevice):
    def __init__(self):
        self.grid: Dict[(int, int), ScreenTile] = defaultdict(lambda: ScreenTile.EMPTY)
        self.ball_pos = None
        self.paddle_pos = None
        self.score = 0

    def get(self, x: int, y: int) -> ScreenTile:
        return self.grid[(x, y)]

    def set(self, x: int, y: int, value: ScreenTile) -> None:
        self.grid[(x, y)] = value

    def io_put(self) -> Generator[None, ScreenTile, None]:
        while True:
            raw_x = yield
            raw_y = yield
            raw_tile = yield
            if raw_x == -1 and raw_y == 0:
                self.score = raw_tile
                continue

            tile = ScreenTile(raw_tile)
            if tile == ScreenTile.BALL:
                self.ball_pos = (raw_x, raw_y)
            elif tile == ScreenTile.H_PADDLE:
                self.paddle_pos = (raw_x, raw_y)

            self.set(raw_x, raw_y, tile)
            print(self)

    def __repr__(self) -> str:
        grid_keys = self.grid.keys()
        if len(grid_keys) == 0:
            return str(ScreenTile.EMPTY)

        max_x = max([x for (x, _) in grid_keys]) + 1
        max_y = max([y for (_, y) in grid_keys]) + 1

        empty_row = [str(ScreenTile.EMPTY)] * max_x
        full_grid = [copy.copy(empty_row) for _ in range(max_y)]

        for (x, y) in grid_keys:
            full_grid[y][x] = str(ScreenTile(self.grid[(x, y)]))
        joined_rows = ["".join(row) for row in full_grid]
        header = f"SCORE: {self.score}"
        joined_rows.insert(0, header)
        footer = f"PADDLE: {self.paddle_pos} BALL: {self.ball_pos}"
        joined_rows.append(footer)
        return "\n".join(joined_rows)


class ArcadeCabinet(InputDevice, OutputDevice):
    def __init__(self, screen: OutputScreen, joystick: JoyStick):
        self.screen = screen
        self.joystick = joystick
        self.screen_passthrough = self.screen.io_put()
        next(self.screen_passthrough)

    def chase_ball(self):
        if self.screen.ball_pos is not None and self.screen.paddle_pos is not None:
            ball_x, ball_y = self.screen.ball_pos
            pad_x, pad_y = self.screen.paddle_pos
            self.joystick.set_pos(JoyStick.LEFT)

            if pad_x > ball_x:
                self.joystick.set_pos(JoyStick.LEFT)
            elif pad_x < ball_x:
                self.joystick.set_pos(JoyStick.RIGHT)
            else:
                self.joystick.set_pos(JoyStick.NEUT)

    def io_put(self) -> Generator[None, ScreenTile, None]:
        while True:
            self.chase_ball()
            screen_put = yield
            self.screen_passthrough.send(screen_put)


with open('input.txt') as INPUT:
    day13_inputs = [int(i) for i in INPUT.read().split(',')]

screen = OutputScreen()
joystick = JoyStick()

cabinet = ArcadeCabinet(screen, joystick)

day13_machine_state = MachineState(day13_inputs, joystick, cabinet)
day13_machine_state.memory[0] = 2
day13_computer = IntCodeComputer(day13_machine_state)

try:
    day13_computer.exec_program()
except HaltException:
    pass


print("=== FINAL SCORE ===")
print(screen)