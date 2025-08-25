import time
from flexprofiler import FlexProfiler


def test_line_level_tracking():
    profiler = FlexProfiler(detailed=False, record_each_call=True)

    @profiler.track(lines=True)
    def foo(x):
        a = x + 1
        time.sleep(0.01)
        b = a * 2
        time.sleep(0.005)
        return b

    # Call function a few times to collect per-line timings
    foo(1)
    foo(2)

    key = 'foo'
    assert key in profiler.line_stats, "Expected line stats for function 'foo' to be recorded"