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
        # Our laser is going to be rotating clockwise, so it's more natural to assume 'increasing'
        # the angle happens clockwise as well, which is backwards from usual way things are done

        return (math.isclose(self.theta, other.theta) and self.r > other.r) or \
               (not math.isclose(self.theta, other.theta) and self.theta < other.theta)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"(θ: {self.theta:.9f} r:{self.r:.9f})"


class AsteroidMap:
    def __init__(self, map: List[List[str]]):
        self.map = map
        self.station_x = -1
        self.station_y = -1

    def build_asteroid_list_relative_to(self, origin_x: int, origin_y: int) -> List[CoordinateOfAsteroid]:
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
        return asteroids

    def count_visible_asteroids(self, origin_x: int, origin_y: int) -> int:
        asteroids = self.build_asteroid_list_relative_to(origin_x, origin_y)
        asteroids.sort()

        visible_asteroids = 1
        current_theta = asteroids[0].theta
        for i in range(1, len(asteroids)):
            if asteroids[i].theta < current_theta:
                current_theta = asteroids[i].theta
                visible_asteroids += 1

        return visible_asteroids

    def find_most_visible_asteroids(self) -> int:
        curr_most_visible = -1

        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[y][x] == '#':
                    this_visible_asteroids = self.count_visible_asteroids(x, -1 * y)
                    if this_visible_asteroids > curr_most_visible:
                        self.station_x = x
                        self.station_y = y
                        curr_most_visible = max(curr_most_visible, this_visible_asteroids)

        return curr_most_visible

    def destroy_asteroids(self):
        # print(f"Station at: ({self.station_x}, {self.station_y})")
        asteroids = self.build_asteroid_list_relative_to(self.station_x, -1 * self.station_y)
        # Remove the asteroid at the station
        asteroids.remove(CoordinateOfAsteroid(0, 0))
        asteroids.sort()

        # We want to start the laser pointing "up"
        starting_laser_theta = math.pi / 2

        def find_starting_idx():
            for i in range(len(asteroids)):
                if math.isclose(asteroids[i].theta, starting_laser_theta):
                    return i

        starting_idx = find_starting_idx()
        num_destroyed = 0
        i = starting_idx
        while len(asteroids) > 1:
            destroyed_asteroid = asteroids.pop(i)
            num_destroyed += 1
            if num_destroyed == 200:
                abs_x = destroyed_asteroid.x + self.station_x
                abs_y = -1 * (destroyed_asteroid.y + -1 * self.station_y)
                print(f"200th asteroid destroyed at ({abs_x}, {abs_y})")
                return

            if i >= len(asteroids):
                i = 0
            while math.isclose(asteroids[i].theta, destroyed_asteroid.theta):
                i = (i + 1) % len(asteroids)


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
assert (8 == test_map1.count_visible_asteroids(3, 4))
assert (8 == test_map1.find_most_visible_asteroids())

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
assert (33 == test_map2.count_visible_asteroids(5, -8))
assert (33 == test_map2.find_most_visible_asteroids())

with open('input.txt') as INPUT:
    day10_map_data = convert_text_to_map(INPUT.read())

day10_asteroid_map = AsteroidMap(day10_map_data)
most_visible_asteroids = day10_asteroid_map.find_most_visible_asteroids()
assert (227 == most_visible_asteroids)

day10_asteroid_map.destroy_asteroids()
