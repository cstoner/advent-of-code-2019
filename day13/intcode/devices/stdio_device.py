from typing import Generator

from . import OutputDevice, InputDevice


class StdIoDevice(InputDevice, OutputDevice):
    def io_get(self) -> Generator[int, None, None]:
        yield int(input())

    def io_put(self) -> Generator[None, int, None]:
        val = yield
        print(val)
