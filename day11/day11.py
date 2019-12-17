#!/usr/bin/env python3
import copy
from collections import defaultdict
from queue import Queue
from typing import List, Dict


class HaltException(Exception):
    def __init__(self, exit_value):
        self.exit_value = exit_value


class WaitingForInputException(Exception):
    pass


class YieldAfterOutputException(Exception):
    pass


class MachineState:
    def __init__(self, memory: List[int], input_stream: Queue = None,
                 output_stream: Queue = None, yield_on_output: bool = False):
        self.pc = 0
        self.memory = memory
        self.yield_on_output = yield_on_output

        # It would make this more flexible to define a custom stream so that we could treat
        # STDIN/STDOUT the same as other streams, but that's probably overkill for now
        self.input_stream = input_stream
        self.output_stream = output_stream

        self.relative_base = 0


class Instruction:
    POSITION_MODE = 0
    IMMEDIATE_MODE = 1
    RELATIVE_MODE = 2

    def __init__(self, mode):
        self.mode = mode
        # The raw register values are stored here
        self.register_values = []
        # When values are read from memory according to their mode, they are stored here
        self.operation_values = []

    def _param_count(self) -> int:
        raise Exception("Parameter count must be specified")

    def exec(self, state: MachineState) -> None:
        raise Exception("Exec must be specified")

    def read_registers(self, state: MachineState):
        self.register_values = state.memory[state.pc:state.pc + self._param_count()]
        mode_copy = self.mode
        for (i, r) in enumerate(self.register_values):
            curr_mode = mode_copy % 10
            mode_copy //= 10

            if curr_mode == self.IMMEDIATE_MODE:
                self.operation_values.append(r)
                continue

            mem_addr = None
            if curr_mode == self.POSITION_MODE:
                mem_addr = r
            elif curr_mode == self.RELATIVE_MODE:
                mem_addr = state.relative_base + r
                self.register_values[i] = mem_addr
            assert (mem_addr is not None)

            if mem_addr >= len(state.memory):
                num_needed = (mem_addr + 1) - len(state.memory)
                state.memory.extend([0] * num_needed)

            self.operation_values.append(state.memory[mem_addr])

        state.pc += self._param_count()


class Add(Instruction):
    def _param_count(self) -> int:
        return 3

    def exec(self, state: MachineState):
        state.memory[self.register_values[2]] = self.operation_values[0] + self.operation_values[1]


class Multiply(Instruction):
    def _param_count(self) -> int:
        return 3

    def exec(self, state: MachineState):
        state.memory[self.register_values[2]] = self.operation_values[0] * self.operation_values[1]


class ReadInput(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
        if state.input_stream is not None:
            if state.input_stream.qsize() == 0:
                # Reset the program counter to retry once input has been supplied
                state.pc -= 2
                raise WaitingForInputException
            state.memory[self.register_values[0]] = state.input_stream.get()
        else:
            state.memory[self.register_values[0]] = int(input("Input: "))


class WriteOutput(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
        if state.output_stream is not None:
            state.output_stream.put(self.operation_values[0])
            if state.yield_on_output:
                raise YieldAfterOutputException()
        else:
            print(self.operation_values[0], end='\n')


class JumpIfTrue(Instruction):
    def _param_count(self) -> int:
        return 2

    def exec(self, state: MachineState):
        if self.operation_values[0] != 0:
            state.pc = self.operation_values[1]


class JumpIfFalse(Instruction):
    def _param_count(self) -> int:
        return 2

    def exec(self, state: MachineState):
        if self.operation_values[0] == 0:
            state.pc = self.operation_values[1]


class LessThan(Instruction):
    def _param_count(self) -> int:
        return 3

    def exec(self, state: MachineState):
        if self.operation_values[0] < self.operation_values[1]:
            state.memory[self.register_values[2]] = 1
        else:
            state.memory[self.register_values[2]] = 0


class Equals(Instruction):
    def _param_count(self) -> int:
        return 3

    def exec(self, state: MachineState):
        if self.operation_values[0] == self.operation_values[1]:
            state.memory[self.register_values[2]] = 1
        else:
            state.memory[self.register_values[2]] = 0


class SetRelativeBase(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
        state.relative_base += self.operation_values[0]


class Halt(Instruction):
    def _param_count(self) -> int:
        return 0

    def exec(self, state: MachineState):
        # print(f"Halting with final memory:\n{state.memory}")
        raise HaltException(state.memory[0])


def read_from_instruction_table(state: MachineState) -> Instruction:
    raw_instruction_value = state.memory[state.pc]
    state.pc += 1

    inst_opcode = raw_instruction_value % 100
    inst_mode = raw_instruction_value // 100

    if inst_opcode == 1:
        return Add(inst_mode)
    elif inst_opcode == 2:
        return Multiply(inst_mode)
    elif inst_opcode == 3:
        return ReadInput(inst_mode)
    elif inst_opcode == 4:
        return WriteOutput(inst_mode)
    elif inst_opcode == 5:
        return JumpIfTrue(inst_mode)
    elif inst_opcode == 6:
        return JumpIfFalse(inst_mode)
    elif inst_opcode == 7:
        return LessThan(inst_mode)
    elif inst_opcode == 8:
        return Equals(inst_mode)
    elif inst_opcode == 9:
        return SetRelativeBase(inst_mode)
    elif inst_opcode == 99:
        return Halt(inst_mode)
    else:
        raise Exception(f"Unknown instruction encountered: {raw_instruction_value}")


def exec_program(machine_state: MachineState) -> None:
    while True:
        # print_state(machine_state)
        inst = read_from_instruction_table(machine_state)
        inst.read_registers(machine_state)
        inst.exec(machine_state)


def print_state(machine_state: MachineState) -> None:
    def chunks(l, n):
        """Yield n number of striped chunks from l."""
        for i in range(0, len(n), l):
            yield n[i:i+l]

    print(f"Program Counter: {machine_state.pc} (instr: {machine_state.memory[machine_state.pc]})")
    print(f"Relative Base: {machine_state.relative_base}")
    print(f"Memory:")
    memory_chunks = list(chunks(10, machine_state.memory))
    for (i, l) in enumerate(memory_chunks):
        print(f"{i*10} - {l}")

    # print(f"Input: {machine_state.input_stream.queue}")
    # print(f"Output: {machine_state.output_stream.queue}")


class RobotVector:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def __init__(self, init_x=0, init_y=0, init_dir=UP):
        self.x: int = init_x
        self.y: int = init_y
        self.dir: int = init_dir

    def turn_right(self):
        self.dir = (self.dir + 1) % 4

    def turn_left(self):
        self.dir = (self.dir + 3) % 4

    def go_forward(self):
        if self.dir == RobotVector.UP:
            self.y += 1
            # print(f"Went up. New coords: ({self.x}, {self.y})")
        elif self.dir == RobotVector.RIGHT:
            self.x += 1
            # print(f"Went right. New coords: ({self.x}, {self.y})")
        elif self.dir == RobotVector.DOWN:
            self.y -= 1
            # print(f"Went down. New coords: ({self.x}, {self.y})")
        elif self.dir == RobotVector.LEFT:
            self.x -= 1
            # print(f"Went left. New coords: ({self.x}, {self.y})")
        else:
            raise Exception("Unknown value for direction")

    def __str__(self):
        if self.dir == RobotVector.UP:
            return '^'
        elif self.dir == RobotVector.RIGHT:
            return '>'
        elif self.dir == RobotVector.DOWN:
            return 'v'
        elif self.dir == RobotVector.LEFT:
            return '<'
        else:
            raise Exception("Unknown value for direction")


class SpaceShipGrid:
    BLACK = 0
    WHITE = 1

    def __init__(self, program: MachineState):
        self.grid: Dict[(int, int), int] = defaultdict(lambda: SpaceShipGrid.BLACK)
        self.robot_location = RobotVector()
        self.program = program

    def get(self, x: int, y: int) -> int:
        return self.grid[(x, y)]

    def set(self, x: int, y: int, value: int) -> None:
        self.grid[(x, y)] = value


    @staticmethod
    def _num_color_to_char(num: int) -> str:
        if num == SpaceShipGrid.BLACK:
            return '.'
        elif num == SpaceShipGrid.WHITE:
            return '#'

    @staticmethod
    def _flatten_grid(grid: List[List[str]]) -> str:
        joined_rows = ["".join(row) for row in grid]
        return "\n".join(joined_rows)

    def __str__(self):
        grid_keys = self.grid.keys()
        if len(grid_keys) == 0:
            return str(self.robot_location)

        x_keys = [x for (x, _) in grid_keys] + [self.robot_location.x]
        y_keys = [y for (_, y) in grid_keys] + [self.robot_location.y]
        min_x = min(x_keys)
        max_x = max(x_keys)
        min_y = min(y_keys)
        max_y = max(y_keys)

        delta_x = abs(max_x - min_x) + 1
        delta_y = abs(max_y - min_y) + 1

        empty_row = [self._num_color_to_char(SpaceShipGrid.BLACK)] * delta_x
        full_grid = [copy.copy(empty_row) for _ in range(delta_y)]

        # "upper left" of grid is (min_x, max_y), so (0, 0) is actually at (0-min_x, max_y)
        origin_0x = 0 - min_x
        origin_0y = max_y

        for (x, y) in grid_keys:
            translated_x = origin_0x + x
            translated_y = origin_0y - y

            full_grid[translated_y][translated_x] = self._num_color_to_char(self.grid[(x, y)])

        robot_x = origin_0x + self.robot_location.x
        robot_y = origin_0y - self.robot_location.y

        full_grid[robot_y][robot_x] = str(self.robot_location)

        return self._flatten_grid(full_grid)

    def run_program(self):
        def exec_program_with_input_supplied_on_demand() -> int:
            while True:
                try:
                    exec_program(self.program)
                except WaitingForInputException:
                    program_input = self.get(self.robot_location.x, self.robot_location.y)
                    self.program.input_stream.put(program_input)
                except YieldAfterOutputException:
                    return self.program.output_stream.get()
        try:
            while True:
                raw_color = exec_program_with_input_supplied_on_demand()
                raw_turn = exec_program_with_input_supplied_on_demand()
                # print("===== BEGIN =====")
                # print(str(self))
                # interp_turn = 'LEFT' if raw_turn == 0 else 'RIGHT'
                # interp_color = self._num_color_to_char(raw_color)
                # print(f"Got Instructions - Color:{interp_color} Turn:{interp_turn}")
                self.set(self.robot_location.x, self.robot_location.y, raw_color)
                if raw_turn == 0:
                    self.robot_location.turn_left()
                elif raw_turn == 1:
                    self.robot_location.turn_right()
                self.robot_location.go_forward()
                # print(str(self))
                # print("===== END =====")

        except HaltException:
            print(f"Painted a total of {len(self.grid.keys())} tiles")






# test_prog1_input = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
# test_prog1 = MachineState(
#     test_prog1_input,
#     Queue(),
#     Queue(),
#     False
# )
# exec_program(test_prog1)

with open('input.txt') as INPUT:
    day11_inputs = [int(i) for i in INPUT.read().split(',')]

day11_machine = MachineState(day11_inputs, Queue(), Queue(), True)

day11_spaceship_grid = SpaceShipGrid(day11_machine)
day11_spaceship_grid.set(0,0, SpaceShipGrid.WHITE)
day11_spaceship_grid.run_program()
print(day11_spaceship_grid)