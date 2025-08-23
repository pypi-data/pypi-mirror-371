import time
import pytest
from flexprofiler import FlexProfiler

def test_simple_func_stats():
    profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)
    @profiler.track
    def simple_func():
        for i in range(2):
            time.sleep(0.01)
    simple_func()
    simple_func()
    assert profiler.calls_count['simple_func'] == 2
    assert profiler.total_time['simple_func'] > 0

def test_class_tracking():
    profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)
    @profiler.track_all_recursive()
    class Foo:
        def __init__(self):
            self.sub_class = Bar()
        def example_method(self):
            self.another_method()
            time.sleep(0.01)
        def another_method(self):
            time.sleep(0.02)
        def calling_subclass_method(self):
            for i in range(2):
                self.sub_class.subclass_method_1()
                self.sub_class.subclass_method_2()
                self.sub_class.subclass_method_3()
    class Bar:
        def subclass_method_1(self):
            time.sleep(0.005)
        def subclass_method_2(self):
            self.a()
            self.b()
        def subclass_method_3(self):
            self.a()
            self.b()
        def a(self):
            time.sleep(0.002)
        def b(self):
            time.sleep(0.001)
    obj = Foo()
    obj.example_method()
    obj.calling_subclass_method()
    # Check that tracked methods are present
    assert 'Foo.example_method' in profiler.calls_count
    assert 'Foo.another_method' in profiler.calls_count
    assert 'Bar.subclass_method_1' in profiler.calls_count
    assert 'Bar.subclass_method_2' in profiler.calls_count
    assert 'Bar.subclass_method_3' in profiler.calls_count
