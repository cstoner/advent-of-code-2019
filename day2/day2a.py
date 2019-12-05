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


# 1202 program alarm, replace input 1 with 12 and 2 with 2
inputs[1] = 12
inputs[2] = 2

exec_program(inputs)

print(f"The value of position 0 after execution: {inputs[0]}")
