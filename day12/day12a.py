#!/usr/bin/env python3
import re
from typing import List


class Vector:
    input_regex = re.compile(r'<x=\s*(-?\d+), y=\s*(-?\d+), z=\s*(-?\d+)>')

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"<x={self.x: >3}, y={self.y: >3}, z={self.z:>3}>"

    def __getitem__(self, key: int):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError(f"Index out of bounds: {key}")

    def __setitem__(self, key: int, value: int):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError(f"Index out of bounds: {key}")

    @classmethod
    def from_str(cls, s: str):
        m = cls.input_regex.match(s)
        x = int(m.groups()[0])
        y = int(m.groups()[1])
        z = int(m.groups()[2])
        return cls(x, y, z)


class Moon:
    def __init__(self, start: Vector = Vector(0, 0, 0)):
        self.position = start
        self.velocity = Vector(0, 0, 0)
        self.acceleration = Vector(0, 0, 0)

    def __repr__(self):
        return f"pos={self.position}, vel={self.velocity}"

    def apply_acceleration(self):
        for i in range(3):
            self.velocity[i] += self.acceleration[i]

    def apply_velocity(self):
        for i in range(3):
            self.position[i] += self.velocity[i]

    def get_energy(self) -> int:
        pot = abs(self.position.x) + abs(self.position.y) + abs(self.position.z)
        kin = abs(self.velocity.x) + abs(self.velocity.y) + abs(self.velocity.z)
        return pot * kin


class GravitySimulation:
    def __init__(self, moons: List[Moon]):
        self.moons = moons
        self.step = 0

    def __repr__(self):
        output_lines = [f"After {self.step} steps:"]
        for moon in self.moons:
            output_lines.append(str(moon))
        return "\n".join(output_lines)

    def _clear_previous_accelerations(self):
        for moon in self.moons:
            moon.acceleration = Vector(0, 0, 0)

    def _apply_gravity(self, moon1: Moon, moon2: Moon):
        for dim in range(3):
            if moon1.position[dim] > moon2.position[dim]:
                moon1.acceleration[dim] -= 1
                moon2.acceleration[dim] += 1
            elif moon1.position[dim] < moon2.position[dim]:
                moon1.acceleration[dim] += 1
                moon2.acceleration[dim] -= 1

    def _calculate_accelerations_for_tick(self):
        for i in range(len(self.moons)):
            for j in range(i, len(self.moons)):
                self._apply_gravity(self.moons[i], self.moons[j])

    def tick(self) -> None:
        self._clear_previous_accelerations()
        self._calculate_accelerations_for_tick()
        for moon in self.moons:
            moon.apply_acceleration()
            moon.apply_velocity()
        self.step += 1

    def total_energy(self) -> int:
        return sum([moon.get_energy() for moon in self.moons])


test_sim1 = GravitySimulation([
    Moon(Vector(-1, 0, 2)),
    Moon(Vector(2, -10, -7)),
    Moon(Vector(4, -8, 8)),
    Moon(Vector(3, 5, -1))
])

for _ in range(10):
    test_sim1.tick()

assert(179 == test_sim1.total_energy())

test_sim2 = GravitySimulation([
    Moon(Vector(-8, -10, 0)),
    Moon(Vector(5, 5, 10)),
    Moon(Vector(2, -7, 3)),
    Moon(Vector(9, -8, -3))
])


for _ in range(100):
    test_sim2.tick()

assert(1940 == test_sim2.total_energy())

day12_sim = None
with open('input.txt') as INPUT:
    moons = []
    for line in INPUT.readlines():
        line.strip()
        if line != "":
            moons.append(Moon(Vector.from_str(line)))

    day12_sim = GravitySimulation(moons)


for _ in range(1000):
    day12_sim.tick()

day12_total_energy = day12_sim.total_energy()
print(f"Total energy after {day12_sim.step} steps: {day12_sim.total_energy()}")
