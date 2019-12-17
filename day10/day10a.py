#!/usr/bin/env python3
import math
from functools import total_ordering
from typing import List


@total_ordering
class CoordinateOfAsteroid:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

        self.theta = math.atan2(y, x)
        self.r = math.sqrt(x ** 2 + y ** 2)

    def __eq__(self, other):
        return math.isclose(self.theta, other.theta) and math.isclose(self.r, other.r)

    def __gt__(self, other):
        # Not sure if it matters, but I want to ensure "close" values of theta always use distance
        return (math.isclose(self.theta, other.theta) and self.r > other.r) or \
               (not math.isclose(self.theta, other.theta) and self.theta > other.theta)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"(θ: {self.theta:.9f} r:{self.r:.9f})"


class AsteroidMap:
    def __init__(self, map: List[List[str]]):
        self.map = map

    def sort_asteroids_by_theta_from(self, origin_x: int, origin_y: int):
        def build_polar_coord_to(asteroid_x: int, asteroid_y: int):
            x_delta = asteroid_x - origin_x
            y_delta = asteroid_y - origin_y

            retval = CoordinateOfAsteroid(x_delta, y_delta)

            return retval

        asteroids = []
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[y][x] == '#':
                    asteroids.append(build_polar_coord_to(x, -1 * y))
        asteroids.sort()
        return asteroids

    def count_visible_asteroids(self, origin_x: int, origin_y: int):
        asteroids = self.sort_asteroids_by_theta_from(origin_x, origin_y)

        asteroid_thetas = set([asteroid.theta for asteroid in asteroids])
        visible_asteroids = 1
        current_theta = asteroids[0].theta
        for i in range(1, len(asteroids)):
            if asteroids[i].theta > current_theta:
                current_theta = asteroids[i].theta
                visible_asteroids += 1

        return visible_asteroids

    def find_most_visible_asteroids(self):
        curr_most_visible = -1

        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[y][x] == '#':
                    this_visible_asteroids = self.count_visible_asteroids(x, -1 * y)
                    if this_visible_asteroids > curr_most_visible:
                        curr_most_visible = max(curr_most_visible, this_visible_asteroids)

        return curr_most_visible


def convert_text_to_map(str_input: str) -> List[List[str]]:
    data_by_row = str_input.strip().split('\n')
    return [[char for char in line] for line in data_by_row]


test_map1 = AsteroidMap(convert_text_to_map("""
.#..#
.....
#####
....#
...##
"""))
assert(8 == test_map1.count_visible_asteroids(3, 4))
assert(8 == test_map1.find_most_visible_asteroids())

test_map2 = AsteroidMap(convert_text_to_map("""
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
"""))
assert(33 == test_map2.count_visible_asteroids(5, -8))
assert(33 == test_map2.find_most_visible_asteroids())


with open('input.txt') as INPUT:
    day10_map_data = convert_text_to_map(INPUT.read())


day10_asteroid_map = AsteroidMap(day10_map_data)
most_visible_asteroids = day10_asteroid_map.find_most_visible_asteroids()

# 224 too low
print(f"The most visible astroids from a single position are: {most_visible_asteroids }")
