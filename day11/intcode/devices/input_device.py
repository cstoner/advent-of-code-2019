#!/usr/bin/env python3
from typing import Generator


class InputDevice:
    def io_get(self) -> Generator[int, None, None]:
        raise NotImplemented("InputDevice.get must be overridden")
