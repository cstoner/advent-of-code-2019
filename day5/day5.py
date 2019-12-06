#!/usr/bin/env python3
from typing import List


class HaltException(Exception):
    def __init__(self, exit_value):
        self.exit_value = exit_value


class MachineState:
    def __init__(self, memory: List[int]):
        self.memory = memory
        self.pc = 0


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
        self.register_values = state.memory[state.pc:state.pc+self._param_count()]
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
        state.memory[self.register_values[0]] = int(input("Input: "))


class WriteOutput(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
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
        print(f"Halting with final memory:\n{state.memory}")
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


def exec_program(memory: List[int]) -> int:
    state = MachineState(memory)

    try:
        while True:
            inst = read_from_instruction_table(state)
            inst.read_registers(state)
            inst.exec(state)
    except HaltException as e:
        return e.exit_value


with open('input.txt') as INPUT:
    inputs = [int(x) for x in INPUT.read().split(',')]


exec_program(inputs)

