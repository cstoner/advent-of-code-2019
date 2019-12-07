#!/usr/bin/env python3
from typing import List, Dict


def build_orbits_from_inputs(inputs: List[str]) -> Dict[str, str or None]:
    orbits = {'COM': None}

    for orbit in inputs:
        (orbitee, orbiter) = orbit.split(')')
        orbits[orbiter.strip()] = orbitee.strip()

    return orbits


def get_path_to_com(orbits: Dict[str, str], start: str) -> List[str]:
    path = []
    curr = start
    while curr != 'COM':
        path.append(orbits[curr])
        curr = orbits[curr]

    return path


def find_path_to_common_parent(path1: List[str], path2: List[str]) -> str:
    prev = ''
    while path1[-1] == path2[-1]:
        prev = path1.pop()
        path2.pop()

    path1.append(prev)
    path2.append(prev)


with open('input.txt') as INPUT:
    inputs = INPUT.readlines()

built_orbits = build_orbits_from_inputs(inputs)
you_path = get_path_to_com(built_orbits, 'YOU')
san_path = get_path_to_com(built_orbits, 'SAN')

find_path_to_common_parent(you_path, san_path)

# Subtracting 2, since we don't have to transfer to our starting planets
print(f"Distance from YOU to SAN: {len(you_path) + len(san_path) - 2}")
