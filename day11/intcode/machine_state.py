from typing import List

from .devices.input_device import InputDevice
from .devices.output_device import OutputDevice


class MachineState:
    def __init__(self, memory: List[int],
                 input_device: InputDevice,
                 output_device: OutputDevice):
        self.pc = 0
        self.relative_base = 0
        self.memory = memory

        self.input_device = input_device.io_get()
        self.output_device = output_device.io_put()
        next(self.output_device)

    def __repr__(self):
        def chunks(n: int, lst: List[int]):
            """Yield n number of striped chunks from list."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        output_lines = [f"Program Counter: {self.pc} (instr: {self.memory[self.pc]})",
                        f"Relative Base: {self.relative_base}",
                        f"Memory:"]

        memory_chunks = list(chunks(10, self.memory))
        for (i, l) in enumerate(memory_chunks):
            output_lines.append(f"{i * 10: >4} - {l}")

        return "\n".join(output_lines)
