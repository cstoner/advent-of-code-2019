from . import instructions
from .instructions.instructions import Instruction
from .machine_state import MachineState


class IntCodeComputer:
    def __init__(self, machine_state: MachineState):
        self.machine_state = machine_state
        self.logger = None

    def read_next_instruction(self) -> (Instruction, int):
        raw_memory = self.machine_state.memory[self.machine_state.pc]
        self.machine_state.pc += 1

        inst = raw_memory % 100
        mode = raw_memory // 100
        return instructions.instruction_table[inst], mode

    def exec_program(self) -> None:
        while True:
            if(self.logger is not None):
                self.logger()

            (inst, mode) = self.read_next_instruction()
            inst.load_registers(mode, self.machine_state)
            inst.exec(self.machine_state)
