#!/usr/bin/env python3


def has_double(val: str):
    prev_char = ''
    curr_run = 0
    for c in val:
        if c != prev_char:
            if curr_run == 2:
                return True
            curr_run = 1
            prev_char = c
        else:
            curr_run += 1

    return curr_run == 2


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


assert valid_pass('112233')
assert not valid_pass('123444')
assert valid_pass('111122')

with open('input.txt') as INPUT:
    (start_range, end_range) = [int(x) for x in INPUT.read().split('-')]

password_count = 0
for i in range(start_range, end_range+1):
    i_str = str(i)
    if valid_pass(i_str):
        password_count += 1


print(f"Number of valid passwords: {password_count}")
