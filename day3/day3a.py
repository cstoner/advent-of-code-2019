#!/usr/bin/env python3
import copy
from functools import total_ordering
from typing import List


@total_ordering
class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def value(self) -> int:
        """The manhattan distance from the origin"""
        return abs(self.x)+abs(self.y)

    def __gt__(self, other) -> bool:
        if self.x > other.x:
            return True
        elif self.x == other.x:
            return self.y > other.y
        else:
            return False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"


@total_ordering
class Line:
    def __init__(self, p1: Point, p2: Point):
        if p1 > p2:
            (p2, p1) = (p1, p2)

        self.p1 = p1
        self.p2 = p2

    def __gt__(self, other):
        if self.p1 > other.p1:
            return True
        elif self.p1 == other.p1:
            return self.p2 > other.p2
        else:
            return False

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f"[{self.p1}, {self.p2}]"

    def __repr__(self):
        return f"[{self.p1}, {self.p2}]"


def construct_lines_from_path_directions(directions: List[str]) -> (List[Line], List[Line]):
    """

    :param directions: list of directions in the form of "R15", "L2", etc where the first letter
                       is a cardinal direction, and the number is the distance
    :return: (horiz_lines, vert_lines) sorted by x axis
    """
    current_point = Point(0, 0)

    vert_lines = []
    horiz_lines = []

    for direction in directions:
        (cardinal_dir, dist) = direction[0], int(direction[1:])
        new_point = copy.copy(current_point)

        if cardinal_dir == 'R':
            new_point.x += dist
            horiz = True
        elif cardinal_dir == 'L':
            new_point.x -= dist
            horiz = True
        elif cardinal_dir == 'U':
            new_point.y += dist
            horiz = False
        elif cardinal_dir == 'D':
            new_point.y -= dist
            horiz = False
        else:
            raise Exception(f"Unknown direction encountered: {cardinal_dir}")

        if horiz:
            horiz_lines.append(Line(current_point, new_point))
        else:
            vert_lines.append(Line(current_point, new_point))

        current_point = new_point

    horiz_lines.sort()
    vert_lines.sort()
    return horiz_lines, vert_lines


def sweep_search_intersections(horiz_lines: List[Line], vert_lines: List[Line]) -> List[Point]:
    """
    :param horiz_lines: list of lines ordered by their leftmost x coordinate
    :param vert_lines: list of lines ordered by their x positions
    :return: list of Point objects represention line intersections
    """
    intersections: List[Point] = []
    # Walk just the vertical portions
    active_horiz = []
    for line in vert_lines:
        active_horiz = list(filter(lambda active_line: active_line.p2 > line.p2, active_horiz))
        # print(f"Current line: {line}")
        while len(horiz_lines) > 0 and horiz_lines[0].p1 < line.p1:
            # print(f"Adding {h2[0]}")
            active_horiz.append(horiz_lines.pop(0))

        # print(f"Active horiz lines: {active_horiz}")
        for active_line in active_horiz:
            if line.p1.y < active_line.p1.y < line.p2.y:
                # print(f"Found Intersection at ({line.p1.x}, {active_line.p1.y})")
                intersections.append(Point(line.p1.x, active_line.p1.y))

    return intersections


def find_intersections(wire1_path: List[str], wire2_path: List[str]) -> List[Point]:
    (h1, v1) = construct_lines_from_path_directions(wire1_path)
    (h2, v2) = construct_lines_from_path_directions(wire2_path)

    return sweep_search_intersections(h1, v2) + sweep_search_intersections(h2, v1)


def find_intersection_dist_closest_to_origin(wire1_path: List[str], wire2_path: List[str]) -> int:
    all_intersections = find_intersections(wire1_path, wire2_path)
    return min([v.value() for v in all_intersections if v.value() is not 0])


# Test inputs given to us
assert find_intersection_dist_closest_to_origin(
    "R8,U5,L5,D3".split(','),
    "U7,R6,D4,L4".split(',')
) == 6
assert find_intersection_dist_closest_to_origin(
    "R75,D30,R83,U83,L12,D49,R71,U7,L72".split(','),
    "U62,R66,U55,R34,D71,R55,D58,R83".split(',')
) == 159
assert find_intersection_dist_closest_to_origin(
    "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51".split(','),
    "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7".split(',')
) == 135


with open("input.txt") as INPUT:
    (wire1, wire2) = INPUT.readlines()

closest_intersection = find_intersection_dist_closest_to_origin(wire1.split(','), wire2.split(','))
print(f"Found closest intersection a distance of {closest_intersection} from the origin")

