#!/usr/bin/env python3

with open('input.txt') as INPUT:
    (start_range, end_range) = [int(x) for x in INPUT.read().split('-')]


def has_double(val: str):
    prev = ''
    for x in val:
        if x == prev:
            return True
        prev = x
    return False


def always_increasing(val: str):
    prev_num = -1
    for x in val:
        num = int(x)
        if num < prev_num:
            return False
        prev_num = num
    return True


def valid_pass(val: str):
    return has_double(val) and always_increasing(val)


assert valid_pass('111111')
assert not valid_pass('223450')
assert not valid_pass('123789')

password_count = 0

for i in range(start_range, end_range+1):
    i_str = str(i)
    if valid_pass(i_str):
        password_count += 1


print(f"Number of valid passwords: {password_count}")