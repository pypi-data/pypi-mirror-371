# Copyright (c) 2016 Alex Sherman
# SPDX-License-Identifier: MIT

from deco import concurrent

BODIES = [90]


@concurrent
def simulate():
    print(BODIES)


def run():
    BODIES.append(210)
    simulate()
    simulate.wait()


if __name__ == "__main__":
    run()
