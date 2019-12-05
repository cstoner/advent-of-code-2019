#!/usr/bin/env python3


def calc_fuel(mass: int) -> int:
    return (mass // 3) - 2


assert calc_fuel(12) == 2
assert calc_fuel(14) == 2
assert calc_fuel(1969) == 654
assert calc_fuel(100756) == 33583

with open('input.txt') as INPUT:
    inputs = INPUT.readlines()

fuel_needs = sum([calc_fuel(int(mass)) for mass in inputs])
print(f"Fuel needs: {fuel_needs}")
