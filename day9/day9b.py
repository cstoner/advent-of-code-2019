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


def exec_program(machine_state: MachineState) -> int or None:
    try:
        while True:
            # print_state("EXECUTING", machine_state)
            inst = read_from_instruction_table(machine_state)
            inst.read_registers(machine_state)
            inst.exec(machine_state)
    except (WaitingForInputException, YieldAfterOutputException, HaltException):
        # Pretty sure this is wrong... would be nice to use yield
        return None


def print_state(label: str, machine_state: MachineState) -> None:
    print(f"State of {label}")
    print(f"Program Counter: {machine_state.pc} (instr: {machine_state.memory[machine_state.pc]})")
    print(f"Memory: {machine_state.memory}")
    print(f"Relative Base: {machine_state.relative_base}")
    # print(f"Input: {machine_state.input_stream.queue}")
    # print(f"Output: {machine_state.output_stream.queue}")


# test_prog1_input = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
# test_prog1 = MachineState(
#     test_prog1_input,
#     Queue(),
#     Queue(),
#     False
# )
# exec_program(test_prog1)

with open('input.txt') as INPUT:
    day9_inputs = [int(i) for i in INPUT.read().split(',')]

input_queue = Queue()
input_queue.put(2)
day9_machine = MachineState(day9_inputs, input_queue, Queue())
exec_program(day9_machine)
print(day9_machine.output_stream.queue)