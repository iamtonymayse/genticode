from __future__ import annotations

from typing import Callable


def detect_flakes(runs: int, runner: Callable[[], bool]) -> tuple[float, int]:
    """Run `runner` N times; it returns True if failed.

    Returns (flake_rate, total_failures).
    """
    fails = 0
    n = max(1, int(runs))
    for _ in range(n):
        if bool(runner()):
            fails += 1
    rate = fails / n
    return rate, fails

