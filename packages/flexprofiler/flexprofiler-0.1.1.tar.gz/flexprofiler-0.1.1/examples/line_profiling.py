"""Example showing line-by-line profiling with flexprofiler.

Run this script to see per-line timing collected by decorating a function
with @track(lines=True).
"""
import time
from flexprofiler import track, stats


@track(lines=True)
def bar(n):
    total = 0
    for i in range(n):
        total += i
        if i % 2 == 0:
            time.sleep(0.001)
        else:
            time.sleep(0.0005)
    return total

@track()
def foo():
    for _ in range(3):
        bar(50)

if __name__ == "__main__":
    foo()

    stats()  # display the profiling statistics