# Copyright (c) 2016 Alex Sherman
# SPDX-License-Identifier: MIT

import time

from deco import concurrent


@concurrent.threaded
def threaded_func():
    time.sleep(0.1)


@concurrent
def mp_func():
    time.sleep(0.1)


def sync(func):
    for _ in range(10):
        func()
    func.wait()


if __name__ == "__main__":
    start = time.time()
    sync(mp_func)
    print("Multiprocess duration:", time.time() - start)
    start = time.time()
    sync(threaded_func)
    print("Threaded duration:", time.time() - start)
