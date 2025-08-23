
from collections import defaultdict
import time
import statistics
class FlexProfiler():
    """A class to track the execution time of functions in a class and build a call graph.
    
    Usage:
    1. Create an instance of FlexProfiler.
    2. Use the `track` method to decorate functions you want to track."""
    def __init__(self, max_depth=10, detailed=False, record_each_call=True):
        self.calls_count = defaultdict(int)
        self.total_time = defaultdict(float)
        self.exec_log = defaultdict(tuple)

        self.max_depth = max_depth
        self.detailed = detailed
        self.record_each_call = record_each_call

        self.call_graph = defaultdict(list)

        self.call_queue = []

    def _update_call_graph(self, call_graph, call_queue, elapsed_time):
        if len(call_queue) == 0:
            return
        current_func = call_queue[0]
        if current_func not in call_graph:
            call_graph[current_func] = {"count": 0, "total_time": 0.0, "children": defaultdict(dict), "exec_log": []}
        if len(call_queue) > 1:
            # Create a nested structure for the call graph
            self._update_call_graph(call_graph[current_func]["children"], call_queue[1:], elapsed_time)
        elif len(call_queue) == 1:
            call_graph[call_queue[0]]["count"] += 1
            call_graph[call_queue[0]]["total_time"] += elapsed_time
            if self.record_each_call:
                call_graph[call_queue[0]]["exec_log"] += [elapsed_time]

    def track(self, func):
        def _track_wrapper(*args, **kwargs):
            level = len(self.call_queue)
            if level < self.max_depth:
                # only track if we are within the max depth
                if args and hasattr(args[0], '__class__'):
                    key = f"{args[0].__class__.__name__}.{func.__name__}"
                else:
                    key = func.__name__
                self.call_queue.append(key)

                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed_time = end_time - start_time

                func_name = key
                if func_name not in self.calls_count:
                    self.calls_count[func_name] = 0
                    self.total_time[func_name] = 0.0
                    self.exec_log[func_name] = []
                
                self.calls_count[func_name] += 1
                self.total_time[func_name] += elapsed_time

                if self.detailed:
                    # build call graph
                    self._update_call_graph(self.call_graph, self.call_queue, elapsed_time)
                # remove the appended
                self.call_queue.pop()
            else:
                result = func(*args, **kwargs)
                
            return result

        return _track_wrapper
    def display_overall_stats(self):
        print("Function Call Statistics:")
        for func_name, count in self.calls_count.items():
            total_time = self.total_time[func_name]
            avg_time = total_time / count if count > 0 else 0
            print(f"{func_name}: {count} calls, Total Time: {total_time:.4f}s, Avg Time: {avg_time:.4f}s")

        print("\n")
    def _stats(self, call_graph, depth=0, is_last_list=[]):

        # ANSI color codes
        RESET = "\033[0m"
        BOLD = "\033[1m"
        # Color gradient from green (fast) to red (slow)
        def color_by_time(avg_time, max_time):
            if max_time == 0:
                return ""
            # Normalize avg_time to [0, 1]
            norm = min(avg_time / max_time, 1.0)
            # Use 256-color ANSI codes for a continuous gradient from green (46) to yellow (226) to red (196)
            # Interpolate between green (46) and red (196) via yellow (226)
            if norm < 0.5:
                # Green to Yellow
                green = 46
                yellow = 226
                color_code = int(green + (yellow - green) * (norm / 0.5))
            else:
                # Yellow to Red
                yellow = 226
                red = 196
                color_code = int(yellow + (red - yellow) * ((norm - 0.5) / 0.5))
            return f"\033[38;5;{color_code}m"

        # Find max avg_time at this level for coloring
        avg_times = [stats.get("total_time", 0.0) / stats.get("count", 1) for stats in call_graph.values() if stats.get("count", 0) > 0]
        max_avg_time = max(avg_times) if avg_times else 0.0

        # Build tree-like indentation with lines
        def get_indent(depth, is_last_list):
            indent = ""
            for d in range(depth):
                if d < depth - 1:
                    indent += "  │  " if not is_last_list[d] else "     "
                else:
                    indent += "  └──" if is_last_list[d] else "  ├──"
            return indent

        def get_spacer(depth, is_last_list):
            spacer = ""
            for d in range(depth):
                if d < depth - 1:
                    spacer += "     " if not is_last_list[d] else "     "
                else:
                    spacer += "     " if is_last_list[d] else " │   "
            return spacer
        # Prepare list of (func_name, stats) and mark which is last at this level
        items = list(call_graph.items())
        n_items = len(items)
        for i, (func_name, stats) in enumerate(items):
            is_last_list_new = is_last_list + [i == n_items - 1]
            indent = get_indent(depth, is_last_list_new)
            spacer = get_spacer(depth, is_last_list_new)
            count = stats.get("count", 0)
            total_time = stats.get("total_time", 0.0)
            avg_time = total_time / count if count > 0 else 0

            color_func = color_by_time(avg_time, max_avg_time)
            color_avg = color_by_time(avg_time, max_avg_time)
            line = (
                f"{indent}{color_func}{BOLD}{func_name}{RESET}: "
                f"{spacer}"
                f"{count} calls, "
                f"Total: {total_time:.4f}s, "
                f"{color_avg}Avg: {avg_time:.4f}s{RESET}"
            )
            if self.record_each_call:
                exec_log = stats.get("exec_log", [])
                if exec_log and len(exec_log) > 1:
                    std_time = statistics.stdev(exec_log)
                    median_time = statistics.median(exec_log)
                    line += f", Std: {std_time:.4f}s, Median: {median_time:.4f}s"
            print(line)
            if "children" in stats:
                self._stats(stats["children"], depth + 1, is_last_list_new if depth > 0 else [])
            pass
    def stats(self):
        if not self.detailed:
            print("Detailed statistics are not enabled. Set `detailed=True` when initializing FlexProfiler.")
            return
        print("Detailed Function Call Statistics:")
        # display the call graph recursively
        self._stats(self.call_graph)

    def track_all(self):
        def decorate(cls):
            for attr in cls.__dict__: # there's probably a better way to do this
                if callable(getattr(cls, attr)):
                    setattr(cls, attr, self.track(getattr(cls, attr)))
            return cls
        return decorate

    def track_all_recursive(self):
        def decorate(cls):
            # Decorate all methods in the class, but skip _track_wrapper
            for attr_name, attr_value in cls.__dict__.items():
                if callable(attr_value) and attr_value.__name__ != "_track_wrapper":
                    setattr(cls, attr_name, self.track(attr_value))

            # Wrap __init__ to decorate all subclass attributes after instantiation
            orig_init = getattr(cls, "__init__", None)
            def new_init(instance, *args, **kwargs):
                if orig_init:
                    orig_init(instance, *args, **kwargs)
                # After __init__, find attributes that are instances of user-defined classes and decorate them
                for attr in dir(instance):
                    if attr.startswith("__"):
                        continue
                    value = getattr(instance, attr)
                    # Only decorate user-defined class instances (skip built-ins)
                    if hasattr(value, "__class__") and hasattr(value.__class__, "__module__"):
                        # Avoid decorating built-in types
                        if not value.__class__.__module__.startswith("builtins"):
                            # Avoid re-decorating
                            if not getattr(value, "_task_tracker_decorated", False):
                                self.track_all_recursive()(value.__class__)
                                setattr(value, "_task_tracker_decorated", True)
            setattr(cls, "__init__", new_init)
            return cls
        return decorate

if __name__ == "__main__":
    # Example usage
    task_tracker = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)

    @task_tracker.track
    def simple_func():
        for i in range(3):
            print(f"Test {i}")
            time.sleep(0.1)

    simple_func()
    simple_func()

    @task_tracker.track_all_recursive()
    class Foo:
        def __init__(self):
            self.sub_class = Bar()
        def example_method(self):
            print("Example method called")
            self.another_method()
            time.sleep(0.1)
        def another_method(self):
            print("Another method called")
            time.sleep(0.2)
        def calling_subclass_method(self):
            for i in range(3):
                self.sub_class.subclass_method_1()
                self.sub_class.subclass_method_2()
                self.sub_class.subclass_method_3()

    # @task_tracker.track_all()
    class Bar:
        def subclass_method_1(self):
            time.sleep(0.05)
        def subclass_method_2(self):
            self.a()
            self.b()
        def subclass_method_3(self):
            self.a()
            self.b()
        def a(self):
            time.sleep(0.02)
        def b(self):
            time.sleep(0.01)

    Foo().example_method()
    Foo().calling_subclass_method()

    task_tracker.display_overall_stats()
    task_tracker.stats()