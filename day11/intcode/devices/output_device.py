#!/usr/bin/env python3
from typing import Generator


class OutputDevice:
    def io_put(self) -> Generator[None, int, None]:
        raise NotImplemented("InputDevice.get must be overridden")
