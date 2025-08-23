import time
from flexprofiler import FlexProfiler

profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)

@profiler.track_all_recursive()
class Foo:
    def example_method(self):
        self.another_method()
        time.sleep(0.1)
    def another_method(self):
        time.sleep(0.2)

Foo().example_method()
Foo().another_method()

# profiler.display_overall_stats()
profiler.stats()