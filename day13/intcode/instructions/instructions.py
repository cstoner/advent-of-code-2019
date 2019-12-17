from ..exceptions.exceptions import IntCodeNotImplemented, HaltException
from ..machine_state import MachineState


class Instruction:
    POSITION_MODE = 0
    IMMEDIATE_MODE = 1
    RELATIVE_MODE = 2

    def __init__(self):
        # Register values are stored here. Useful for resolving memory addresses
        self.register_values = []
        # When values are read from memory according to their mode they are stored here
        self.operation_values = []

    def _param_count(self) -> int:
        raise IntCodeNotImplemented("Parameter count must be specified")

    def exec(self, state: MachineState) -> None:
        raise IntCodeNotImplemented("Exec must be specified")

    def load_registers(self, state: MachineState, mode: int):
        self.operation_values = []
        self.register_values = state.memory[state.pc:state.pc + self._param_count()]
        for (i, r) in enumerate(self.register_values):
            curr_mode = mode % 10
            mode //= 10

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
        state.memory[self.register_values[0]] = next(state.input_device)


class WriteOutput(Instruction):
    def _param_count(self) -> int:
        return 1

    def exec(self, state: MachineState):
        state.output_device.send(self.operation_values[0])


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


