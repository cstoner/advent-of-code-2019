#!/usr/bin/env python3
from typing import Generator

from ..exceptions import IntCodeNotImplemented


class InputDevice:
    def io_get(self) -> Generator[int, None, None]:
        while True:
            yield
            raise IntCodeNotImplemented()
