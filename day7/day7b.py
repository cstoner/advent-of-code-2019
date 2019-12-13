#!/usr/bin/env python3
import copy
from itertools import permutations
from queue import Queue
from typing import List


class HaltException(Exception):
    def __init__(self, exit_value):
        self.exit_value = exit_value


class WaitingForInputException(Exception):
    pass


class YieldAfterOutputException(Exception):
    pass


class MachineState:
    def __init__(self, memory: List[int], input_stream: Queue = None,
                 output_stream: Queue = None):
        self.pc = 0
        self.memory = memory
        # It would make this more flexible to define a custom stream so that we could treat
        # STDIN/STDOUT the same as other streams, but that's probably overkill for now
        self.input_stream = input_stream
        self.output_stream = output_stream


class Instruction:
    POSITION_MODE = 0
    IMMEDIATE_MODE = 1

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
        for r in self.register_values:
            curr_mode = mode_copy % 10
            mode_copy //= 10

            if curr_mode == self.POSITION_MODE:
                self.operation_values.append(state.memory[r])
            elif curr_mode == self.IMMEDIATE_MODE:
                self.operation_values.append(r)

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
            state.memory[self.register_values[0]] = state.input_stream.get()
        else:
            state.memory[self.register_values[0]] = int(input("Input: "))


class WriteOutput(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
        if state.output_stream is not None:
            state.output_stream.put(self.operation_values[0])
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
    elif inst_opcode == 99:
        return Halt(inst_mode)
    else:
        raise Exception(f"Unknown instruction encountered: {raw_instruction_value}")


def exec_program(machine_state: MachineState) -> int or None:
    try:
        while True:
            # print_state("EXECUTING", machine_state)
            inst = read_from_instruction_table(machine_state)
            inst.read_registers(machine_state)
            inst.exec(machine_state)
    except (WaitingForInputException, YieldAfterOutputException):
        # Pretty sure this is wrong... would be nice to use yield
        return None


def print_state(label: str, machine_state: MachineState) -> None:
    print(f"State of {label}")
    print(f"Program Counter: {machine_state.pc} (instr: {machine_state.memory[machine_state.pc]})")
    print(f"Memory: {machine_state.memory}")
    print(f"Input: {machine_state.input_stream.queue}")
    print(f"Output: {machine_state.output_stream.queue}")


def search_for_largest_output(initial_input: List[int]):
    max_value = -1
    for perm in permutations([5, 6, 7, 8, 9]):
        (a_init, b_init, c_init, d_init, e_init) = perm

        a_state = MachineState(copy.copy(initial_input), Queue(), Queue())
        a_state.input_stream.put(a_init)
        a_state.input_stream.put(0)

        # One pretty major downside to this approach is that we are adding fake info to the
        # output of the previous stream
        b_state = MachineState(copy.copy(initial_input), a_state.output_stream, Queue())
        b_state.input_stream.put(b_init)

        c_state = MachineState(copy.copy(initial_input), b_state.output_stream, Queue())
        c_state.input_stream.put(c_init)

        d_state = MachineState(copy.copy(initial_input), c_state.output_stream, Queue())
        d_state.input_stream.put(d_init)

        e_state = MachineState(copy.copy(initial_input), d_state.output_stream,
                               a_state.input_stream)
        e_state.input_stream.put(e_init)
        try:
            while True:
                exec_program(a_state)
                exec_program(b_state)
                exec_program(c_state)
                exec_program(d_state)
                exec_program(e_state)
                max_value = max(e_state.output_stream.queue[0], max_value)
        except HaltException as e:
            pass

    print(f"After searching all permutations, got a max value of {max_value}")


# Expect 139629729
# search_for_largest_output([3, 26, 1001, 26, -4, 26, 3, 27, 1002, 27, 2, 27, 1, 27, 26,
#                            27, 4, 27, 1001, 28, -1, 28, 1005, 28, 6, 99, 0, 0, 5])
# Expect 18216
# search_for_largest_output(
#     [3, 52, 1001, 52, -5, 52, 3, 53, 1, 52, 56, 54, 1007, 54, 5, 55, 1005, 55, 26, 1001, 54,
#      -5, 54, 1105, 1, 12, 1, 53, 54, 53, 1008, 54, 0, 55, 1001, 55, 1, 55, 2, 53, 55, 53, 4,
#      53, 1001, 56, -1, 56, 1005, 56, 6, 99, 0, 0, 0, 0, 10])

with open('input.txt') as INPUT:
    inputs = [int(i) for i in INPUT.read().split(',')]

search_for_largest_output(inputs)
