# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

import time

from deco import concurrent, synchronized


@concurrent
def test(sleep_time, i):
    time.sleep(sleep_time)
    return i


@synchronized
def test_size(size):
    results = {}
    for i in range(size):
        results[i] = test(time_duration, i)
    print(results)


SIZE = 100

def main():
    global time_duration
    processes = [1, 2, 3, 4]
    times = [0, 0.005, 0.01, 0.05, 0.1]  # 0.25]
    for process_count in processes:
        for time_duration in times:
            test.processes = process_count
            test.p = None
            test_size(SIZE)
            exit()
            print(process_count, time_duration)


if __name__ == "__main__":
    main()
