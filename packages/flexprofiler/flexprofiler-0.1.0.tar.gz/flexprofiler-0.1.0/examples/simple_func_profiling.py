import time
from flexprofiler import FlexProfiler

profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)

@profiler.track
def simple_func():
    for i in range(3):
        time.sleep(0.1)

simple_func()
simple_func()

# profiler.display_overall_stats()
profiler.stats()