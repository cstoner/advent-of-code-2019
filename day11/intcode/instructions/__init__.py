from typing import Dict

from .instructions import Instruction, Add, Multiply, ReadInput, \
    WriteOutput, JumpIfTrue, JumpIfFalse, LessThan, Equals, SetRelativeBase, Halt

instruction_table: Dict[int, Instruction] = {
    1: Add(),
    2: Multiply(),
    3: ReadInput(),
    4: WriteOutput(),
    5: JumpIfTrue(),
    6: JumpIfFalse(),
    7: LessThan(),
    8: Equals(),
    9: SetRelativeBase(),
    99: Halt(),
}
