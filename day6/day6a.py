#!/usr/bin/env python3
from typing import List, Dict


def build_orbits_from_inputs(orbit_inputs: List[str]) -> Dict[str, str or None]:
    orbits = {'COM': None}

    for orbit in orbit_inputs:
        (orbitee, orbiter) = orbit.split(')')
        orbits[orbiter.strip()] = orbitee.strip()

    return orbits


def calculate_orbital_checksum(orbits: Dict[str, str or None]) -> int:
    memoized_orbits = {'COM': 0}

    def calc_orbit_recursive(orbit: str) -> int:
        if orbit in memoized_orbits:
            return memoized_orbits[orbit]
        else:
            orbitee_distance = calc_orbit_recursive(orbits[orbit])
            memoized_orbits[orbit] = orbitee_distance + 1
            return memoized_orbits[orbit]

    all_orbit_distances = [calc_orbit_recursive(orbit) for orbit in orbits.keys()]
    return sum(all_orbit_distances)


with open('input.txt') as INPUT:
    inputs = INPUT.readlines()

all_orbits = build_orbits_from_inputs(inputs)
print(f"Orbital checksum: {calculate_orbital_checksum(all_orbits)}")
