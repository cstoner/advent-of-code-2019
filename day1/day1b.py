#!/usr/bin/env python3


def calc_fuel(module_mass: int) -> int:
    return (module_mass // 3) - 2


# Inputs from problem prompt
assert calc_fuel(12) == 2
assert calc_fuel(14) == 2
assert calc_fuel(1969) == 654
assert calc_fuel(100756) == 33583


def calc_fuel_for_fuel(fuel_mass: int) -> int:
    fuel_fuel = calc_fuel(fuel_mass)
    if fuel_fuel <= 0:
        return 0

    return fuel_fuel + calc_fuel_for_fuel(fuel_fuel)


# Inputs from problem prompt
assert calc_fuel_for_fuel(2) == 0
assert calc_fuel_for_fuel(654) == 216 + 70 + 21 + 5
assert calc_fuel_for_fuel(33583) == 11192 + 3728 + 1240 + 411 + 135 + 43 + 12 + 2


def total_fuel_needs(module_mass: int) -> int:
    fuel_needs = calc_fuel(module_mass)
    fuel_fuel_needs = calc_fuel_for_fuel(fuel_needs)

    return fuel_needs + fuel_fuel_needs


# Inputs from problem prompt
assert total_fuel_needs(14) == 2
assert total_fuel_needs(1969) == 966
assert total_fuel_needs(100756) == 50346

with open('input.txt') as INPUT:
    inputs = INPUT.readlines()

total_fuel = sum([total_fuel_needs(int(module_mass)) for module_mass in inputs])

print(f"Fuel and fuel for fuel needs: {total_fuel}")
