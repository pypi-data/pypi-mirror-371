"""FlexProfiler

Lightweight function/method execution time tracker and optional call-graph
builder for simple profiling and inspection during development.

This module exposes the ``FlexProfiler`` class which can be used as a
decorator factory to measure execution time of functions and methods. When
initialized with ``detailed=True`` it will also build a nested call graph
showing parent/child relationships between tracked calls.

The implementation is intentionally small and dependency-free so it can be
embedded in scripts or small projects without extra requirements.
"""

from collections import defaultdict
import time
import statistics
import inspect
import sys


# Color gradient from green (fast) to red (slow)
def color_by_time(avg_time, max_time):
    """Return an ANSI 256-color escape sequence representing relative cost.

    Colors are interpolated from green (fast) through yellow to red (slow)
    based on the ratio ``avg_time / max_time``.

    Parameters
    ----------
    avg_time : float
        Average execution time for a function (seconds).
    max_time : float
        Maximum average time observed at the same level. If zero, an empty
        string is returned (no coloring).

    Returns
    -------
    str
        ANSI escape prefix (e.g. "\033[38;5;196m") or empty string when
        coloring should be skipped.
    """
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


# Build tree-like indentation with lines
def get_indent(depth, is_last_list, code=False):
    """Return a tree-like indent string for a node at ``depth``.

    The function generates characters such as '│', '├──' and '└──' to make a
    readable ASCII-art tree when printing nested call graphs.

    Parameters
    ----------
    depth : int
        The nesting level (0 for root).
    is_last_list : Sequence[bool]
        Booleans indicating whether each ancestor at that depth was the last
        sibling (controls whether vertical lines are drawn).
    code : bool
        Whether to use code block indentation.

    Returns
    -------
    str
        The indentation prefix for the current node.
    """
    indent = ""
    for d in range(depth):
        if d < depth - 1:
            indent += "  │  " if not is_last_list[d] else "     "
        elif not code:
            indent += "  └──" if is_last_list[d] else "  ├──"
        else:
            indent += "     " if is_last_list[d] else "  │  "
    return indent


def get_spacer(before_spacer, max_length):
    """Create a spacer of box-drawing characters to align columns when printing.

    Parameters
    ----------
    before_spacer : str
        The left-hand text whose length is used to compute remaining space.
    max_length : int
        The maximum observed length of the left-hand column.

    Returns
    -------
    str
        A string of '─' characters used as a visual spacer.
    """
    spacer = "─" * (max_length + 3 - len(before_spacer))

    return spacer


class FlexProfiler:
    """Simple profiler that records call counts and timings, and optionally a call graph.

    The profiler can be used either by creating an instance and using the
    returned ``track`` decorator, or by importing the module-level convenience
    instance in ``default_profiler`` which exposes ``track`` and ``stats``.

    Parameters
    ----------
    detailed : bool, optional
        When True the profiler will build a nested call graph that shows
        parent/child relationships and per-call timings. When False only
        aggregate counts and total times are recorded. Default: False.
    record_each_call : bool, optional
        When True the profiler keeps a per-function list of each recorded
        elapsed time (useful for computing standard deviation/median).
        May increase memory usage for hot functions. Default: True.

    Attributes
    ----------
    calls_count : defaultdict
        Mapping function name -> integer call count.
    total_time : defaultdict
        Mapping function name -> accumulated time (seconds).
    exec_log : defaultdict
        Mapping function name -> list of individual elapsed times (when
        ``record_each_call`` is True).

    Examples
    --------
    >>> profiler = FlexProfiler(detailed=True)
    >>> @profiler.track(max_depth=3)
    ... def work():
    ...     time.sleep(0.01)
    >>> work()
    >>> profiler.stats(simple=True)
    """

    def __init__(self, detailed=False, record_each_call=True):
        self.exec_log = defaultdict(tuple)

        self.detailed = detailed
        self.record_each_call = record_each_call

        self.call_graph = defaultdict(list)

        self.call_queue = []
        # Per-function, per-line accumulated times: {func_key: {lineno: {"count", "elapsed", "exec_log", "children"}}}
        self.line_stats = defaultdict(
            lambda: defaultdict(
                lambda: {"count": 0, "total_time": 0.0, "exec_log": [], "children": []}
            )
        )

    def _update_call_graph(self, call_graph, call_queue, elapsed_time):
        """Recursively update the nested call-graph structure.

        This internal helper walks the list of function keys in ``call_queue``
        and updates the provided ``call_graph`` mapping with counts,
        accumulated time and per-call execution logs.

        Parameters
        ----------
        call_graph : dict
            Nested mapping representing the current call-graph node children.
        call_queue : list[str]
            Ordered list of function keys representing the active call stack
            (root first).
        elapsed_time : float
            The elapsed time for the leaf call to add (seconds).
        """
        if len(call_queue) == 0:
            return
        current_func = call_queue[0]
        if current_func not in call_graph:
            call_graph[current_func] = {
                "count": 0,
                "total_time": 0.0,
                "children": defaultdict(dict),
                "exec_log": [],
            }
        if len(call_queue) > 1:
            # Create a nested structure for the call graph
            self._update_call_graph(
                call_graph[current_func]["children"], call_queue[1:], elapsed_time
            )
        elif len(call_queue) == 1:
            call_graph[call_queue[0]]["count"] += 1
            call_graph[call_queue[0]]["total_time"] += elapsed_time
            if self.record_each_call:
                call_graph[call_queue[0]]["exec_log"] += [elapsed_time]

    def track(
        self,
        func=None,
        *,
        max_depth=10,
        arg_sensitive=None,
        include=None,
        exclude=None,
        lines=False,
    ):
        """Decorator factory to measure execution time of functions.

        Can be used either with or without arguments::

            @profiler.track
            def f(...):
                ...

            @profiler.track(max_depth=3, arg_sensitive=['foo'])
            def g(...):
                ...

        Parameters
        ----------
        func : callable or None
            When used as ``@profiler.track`` this will be the decorated
            function. When using keyword arguments this parameter is ``None``
            and the function is provided to the returned decorator.
        max_depth : int
            Maximum call depth to record in the call-graph. Deeper calls are
            still executed but not recorded when the depth limit is reached.
        arg_sensitive : Optional[Sequence[str]]
            List of function names for which the argument values should be
            included in the recorded key (useful when the same function is
            used with different inputs and you want to differentiate them).
        include : Optional[Sequence[str]]
            If provided only functions with names in this collection are
            tracked by this decorator.
        exclude : Optional[Sequence[str]]
            If provided functions whose names are in this collection are
            skipped by this decorator.

        Returns
        -------
        callable
            A decorator that wraps the target function and records timing
            and call-graph information according to the profiler configuration.
        """

        def decorator(inner_func):
            def _track_wrapper(*args, **kwargs):
                func_name_base = inner_func.__name__
                # Handle include/exclude logic
                if include is not None and func_name_base not in include:
                    return inner_func(*args, **kwargs)
                if exclude is not None and func_name_base in exclude:
                    return inner_func(*args, **kwargs)
                level = len(self.call_queue)
                is_arg_sensitive = arg_sensitive and (func_name_base in arg_sensitive)
                if level < max_depth:
                    # Determine whether this is a bound method by checking the
                    # wrapped function signature: treat as method only when
                    # the first parameter is named 'self' and an argument was
                    # provided.
                    try:
                        sig = inspect.signature(inner_func)
                        params = list(sig.parameters.keys())
                    except Exception:
                        params = []

                    if params and params[0] == "self" and args:
                        key_base = f"{args[0].__class__.__name__}.{func_name_base}"
                    else:
                        key_base = func_name_base
                    if is_arg_sensitive:
                        sig = inspect.signature(inner_func)
                        bound_args = sig.bind(*args, **kwargs)
                        bound_args.apply_defaults()
                        args_str = ", ".join(
                            f"{name}={value!r}"
                            for name, value in bound_args.arguments.items()
                            if name != "self"
                        )
                        key_args = f"{key_base}({args_str})"
                        key = key_args
                    else:
                        key = key_base
                    self.call_queue.append(key)

                    # Option A: line-by-line tracing enabled
                    if lines:
                        import linecache

                        target_code = inner_func.__code__
                        # Per-call temporary storage for this invocation
                        curr_frame_states = {}

                        def _global_tracer(frame, event, arg):
                            # Only instrument frames that belong to the target function
                            if frame.f_code is not target_code:
                                return None

                            now = time.perf_counter()

                            if event == "call":
                                # Initialize tracking state for this frame
                                curr_frame_states[frame] = {
                                    "last_time": now,
                                    "last_line": frame.f_lineno,
                                }
                                return _global_tracer

                            if event == "line":
                                st = curr_frame_states.get(frame)
                                if st is None:
                                    curr_frame_states[frame] = {
                                        "last_time": now,
                                        "last_line": frame.f_lineno,
                                    }
                                    return _global_tracer

                                elapsed = now - st["last_time"]
                                lineno = st["last_line"]
                                # Store source line content (strip trailing newline)
                                src = linecache.getline(
                                    frame.f_code.co_filename, lineno
                                ).rstrip("\n")
                                if src:
                                    if src.strip()[0] != "@":
                                        self.line_stats[key][lineno]["content"] = src
                                        # Accumulate per-line totals for this function key
                                        self.line_stats[key][lineno]["total_time"] += (
                                            elapsed
                                        )
                                        self.line_stats[key][lineno]["count"] += 1
                                # Update last seen
                                st["last_time"] = now
                                st["last_line"] = frame.f_lineno
                                # continue tracing this frame
                                return _global_tracer

                            if event == "return":
                                st = curr_frame_states.pop(frame, None)
                                if st is not None:
                                    elapsed = now - st["last_time"]
                                    lineno = st["last_line"]
                                    self.line_stats[key][lineno]["total_time"] += (
                                        elapsed
                                    )
                                    self.line_stats[key][lineno]["count"] += 1
                                    src = linecache.getline(
                                        frame.f_code.co_filename, lineno
                                    ).rstrip("\n")
                                    if src:
                                        self.line_stats[key][lineno]["content"] = src

                                return _global_tracer

                            return None

                        prev_tracer = sys.gettrace()

                        try:
                            sys.settrace(_global_tracer)
                            start_time = time.perf_counter()
                            result = inner_func(*args, **kwargs)
                            end_time = time.perf_counter()
                        finally:
                            # Restore previous tracer
                            sys.settrace(prev_tracer)

                    else:
                        start_time = time.perf_counter()
                        result = inner_func(*args, **kwargs)
                        end_time = time.perf_counter()

                    elapsed_time = end_time - start_time

                    if self.detailed:
                        self._update_call_graph(
                            self.call_graph, self.call_queue, elapsed_time
                        )
                    self.call_queue.pop()
                else:
                    result = inner_func(*args, **kwargs)
                return result

            return _track_wrapper

        if func is None:
            return decorator
        else:
            return decorator(func)

    def _stats(self, call_graph, depth=0, is_last_list=[], unit: str = "s"):
        """Return a list of formatted (left, right) column tuples for printing.

        The helper prepares the strings for each node in the nested
        ``call_graph`` structure in a pre-order traversal. Each returned
        element is a tuple ``(left_text, right_text)`` where the left portion
        contains indentation and the function name (with coloring), and the
        right portion contains timing summaries.

        Parameters
        ----------
        call_graph : dict
            Mapping of function name -> stats dict typically produced by
            ``_update_call_graph``.
        depth : int
            Current recursion depth used to compute indentation.
        is_last_list : list[bool]
            Booleans used to determine connector characters for ancestors.
        unit : str
            The time unit to use for displaying timings (e.g., "m", "s", "ms", "us").

        Returns
        -------
        list[tuple[str, str]]
            A sequence of (left_column, right_column) strings ready for
            alignment and printing.
        """
        # ANSI color codes
        RESET = "\033[0m"
        BOLD = "\033[1m"
        ITALIC = "\033[3m"

        if unit == "h":
            scale = 1 / 3600.0
        if unit == "m":
            scale = 1 / 60.0
        elif unit == "s":
            scale = 1.0
        elif unit == "ms":
            scale = 1000.0
        elif unit == "us":
            scale = 1000000.0
        else:
            raise ValueError(f"Unsupported time unit '{unit}'")

        # Find max avg_time at this level for coloring
        avg_times = [
            scale * stats.get("total_time", 0.0) / stats.get("count", 1)
            for stats in call_graph.values()
            if stats.get("count", 0) > 0
        ]
        max_avg_time = max(avg_times) if avg_times else 0.0

        # Prepare list of (func_name, stats) and mark which is last at this level
        nodes = list(call_graph.items())
        n_items = len(nodes)

        lines_content = []
        for i, (func_name, stats) in enumerate(nodes):
            is_last_list_new = is_last_list + [i == n_items - 1]
            indent = get_indent(depth, is_last_list_new)
            count = stats.get("count", 0)
            total_time = stats.get("total_time", 0.0) * scale
            avg_time = total_time / count if count > 0 else 0

            color_func = color_by_time(avg_time, max_avg_time)
            color_avg = color_by_time(avg_time, max_avg_time)

            before_spacer = f"{indent}{color_func}{BOLD}{func_name}{RESET}: "
            after_spacer = f"{count} calls, {total_time:.2f}{unit}, {color_avg}Avg: {avg_time:.2f}{unit}{RESET}"

            if self.record_each_call:
                exec_log = stats.get("exec_log", [])
                if exec_log and len(exec_log) > 1:
                    std_time = statistics.stdev(exec_log) * scale
                    median_time = statistics.median(exec_log) * scale
                    after_spacer += (
                        f", Std: {std_time:.2f}{unit}, Median: {median_time:.2f}{unit}"
                    )

            lines_content.append((before_spacer, after_spacer))

            if func_name in self.line_stats:
                # print times line by line (sorted by line number)
                l_indent = get_indent(depth, is_last_list_new, code=True)
                for line_num, l_stats in sorted(self.line_stats[func_name].items()):
                    content = l_stats.get("content") or ""
                    # Show line number then content; keep original leading whitespace
                    l_before_spacer = f"{l_indent}{ITALIC}{line_num}{RESET}: {content}"
                    count = l_stats.get("count", 0)
                    total = l_stats.get("total_time", 0.0) * scale
                    avr_line_time = total / count if count > 0 else 0.0
                    l_after_spacer = f"{count} calls, {total:.2f}{unit}, Avg: {avr_line_time:.2f}{unit}"
                    lines_content.append((l_before_spacer, l_after_spacer))

            if "children" in stats:
                lines_content.extend(
                    self._stats(
                        stats["children"],
                        depth + 1,
                        is_last_list_new if depth > 0 else [],
                        unit=unit,
                    )
                )

        return lines_content

    def stats(self, unit: str = "ms"):
        """Print either a simple flat report or a detailed call-graph report.

        Parameters
        ----------
        unit : str (default: "ms")
            The time unit to use for displaying timings (e.g., "m", "s", "ms", "us").
        """
        if not self.detailed:
            print(
                "Detailed statistics are not enabled. Set `detailed=True` when initializing FlexProfiler."
            )
            return
        print("Detailed Function Call Statistics:")
        # display the call graph recursively

        lines_content = self._stats(self.call_graph, unit=unit)

        max_length = max([len(before_spacer) for before_spacer, _ in lines_content])
        for before_spacer, after_spacer in lines_content:
            spacer = get_spacer(before_spacer, max_length)
            line = f"{before_spacer}{spacer}{after_spacer}"
            print(line)

    def track_all(self, max_depth=5, arg_sensitive=None, include=None, exclude=None):
        """Class decorator that applies ``track`` to all suitable methods.

        This convenience decorator iterates over attributes defined on the
        class and replaces callables with their tracked equivalents. It also
        wraps ``__init__`` so that instances created afterwards will have
        any non-builtins attribute classes recursively decorated as well.

        Parameters
        ----------
        max_depth, arg_sensitive, include, exclude
            Same semantics as :meth:`track` and forwarded to each applied
            decorator.
        """

        def decorate(cls):
            for attr_name, attr_value in cls.__dict__.items():
                if callable(attr_value) and attr_value.__name__ != "_track_wrapper":
                    method_name = attr_name
                    if include is not None and method_name not in include:
                        continue
                    if exclude is not None and method_name in exclude:
                        continue
                    setattr(
                        cls,
                        attr_name,
                        self.track(
                            attr_value,
                            max_depth=max_depth,
                            arg_sensitive=arg_sensitive,
                            include=include,
                            exclude=exclude,
                        ),
                    )

            orig_init = getattr(cls, "__init__", None)

            def new_init(instance, *args, **kwargs):
                if orig_init:
                    orig_init(instance, *args, **kwargs)
                for attr in dir(instance):
                    if attr.startswith("__"):
                        continue
                    value = getattr(instance, attr)
                    if hasattr(value, "__class__") and hasattr(
                        value.__class__, "__module__"
                    ):
                        if not value.__class__.__module__.startswith("builtins"):
                            if not getattr(value, "_task_tracker_decorated", False):
                                self.track_all(
                                    max_depth=max_depth,
                                    arg_sensitive=arg_sensitive,
                                    include=include,
                                    exclude=exclude,
                                )(value.__class__)
                                setattr(value, "_task_tracker_decorated", True)

            setattr(cls, "__init__", new_init)
            return cls

        return decorate


if __name__ == "__main__":
    # Example usage
    task_tracker = FlexProfiler(detailed=True, record_each_call=True)

    @task_tracker.track(max_depth=5)
    def simple_func():
        for i in range(3):
            print(f"Test {i}")
            time.sleep(0.1)

    simple_func()
    simple_func()

    @task_tracker.track_all(max_depth=3, arg_sensitive=["subclass_method_2"])
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
                self.sub_class.subclass_method_2(i)
                self.sub_class.subclass_method_3()

    class Bar:
        def subclass_method_1(self):
            time.sleep(0.05)

        def subclass_method_2(self, i):
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

    task_tracker.stats()
