#!/usr/bin/env python3
from enum import Enum
from typing import List


class Opcode(Enum):
    add = 1
    multiply = 2
    exit = 99


def exec_program(memory: List[int]) -> List[int]:
    inst = Opcode(memory[0])
    pc: int = 1

    while inst != Opcode.exit:
        (r1, r2, out) = memory[pc:pc + 3]
        pc += 3

        (r1_val, r2_val) = (memory[r1], memory[r2])

        if inst == Opcode.add:
            memory[out] = r1_val + r2_val
        elif inst == Opcode.multiply:
            memory[out] = r1_val * r2_val

        inst = Opcode(memory[pc])
        pc += 1

    return memory


assert exec_program([1, 0, 0, 0, 99]) == [2, 0, 0, 0, 99]
assert exec_program([2, 3, 0, 3, 99]) == [2, 3, 0, 6, 99]
assert exec_program([2, 4, 4, 5, 99, 0]) == [2, 4, 4, 5, 99, 9801]
assert exec_program([1, 1, 1, 4, 99, 5, 6, 0, 99]) == [30, 1, 1, 4, 2, 5, 6, 0, 99]


with open('input.txt') as INPUT:
    inputs = [int(x) for x in INPUT.read().split(',')]


def search_for_inputs(exit_condition: int) -> (int, int):
    for i in range(100):
        for j in range(100):
            program = inputs.copy()
            program[1] = i
            program[2] = j

            exec_program(program)
            if program[0] == exit_condition:
                return i, j

    return -1, -1


EXIT_CONDITION = 19690720
(noun, verb) = search_for_inputs(EXIT_CONDITION)
exception_code = noun * 100 + verb
print(f"The (noun, verb) values that result in a result of {EXIT_CONDITION} is {exception_code}")
