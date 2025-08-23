# flexprofiler

A flexible profiling utility for Python.

## Installation

```bash
pip install flexprofiler
```

## Usage Examples

### 1. Tracking a Simple Function

```python
import time
from flexprofiler import FlexProfiler

profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)

@profiler.track
def simple_func():
    for i in range(3):
        time.sleep(0.1)

simple_func()
simple_func()

profiler.stats()
```

#### Output

<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!-- This file was created with the aha Ansi HTML Adapter. https://github.com/theZiz/aha -->
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="application/xml+xhtml; charset=UTF-8"/>
<title>stdin</title>
</head>
<body>
<pre>
Detailed Function Call Statistics:
<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">simple_func</span>: 2 calls, Total: 0.6008s, <span style="color:#ff0000;">Avg: 0.3004s</span>, Std: 0.0000s, Median: 0.3004s
</pre>
</body>
</html>

### 2. Tracking All Methods in a Class

```python
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

profiler.stats()
```

output:
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!-- This file was created with the aha Ansi HTML Adapter. https://github.com/theZiz/aha -->
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="application/xml+xhtml; charset=UTF-8"/>
<title>stdin</title>
</head>
<body>
<pre>
Detailed Function Call Statistics:
<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Foo.example_method</span>: 1 calls, Total: 0.3003s, <span style="color:#ff0000;">Avg: 0.3003s</span>
  └──<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Foo.another_method</span>:      1 calls, Total: 0.2002s, <span style="color:#ff0000;">Avg: 0.2002s</span>
<span style="color:#ffaf87;"></span><span style="font-weight:bold;color:#ffaf87;">Foo.another_method</span>: 1 calls, Total: 0.2001s, <span style="color:#ffaf87;">Avg: 0.2001s</span>
</pre>
</body>
</html>


### 3. Tracking All Methods in a Class Recursively

```python
import time
from flexprofiler import FlexProfiler

profiler = FlexProfiler(max_depth=5, detailed=True, record_each_call=True)

@profiler.track_all_recursive()
class Foo:
    def __init__(self):
        self.sub_class = Bar()
    def example_method(self):
        self.another_method()
        time.sleep(0.1)
    def another_method(self):
        time.sleep(0.2)
    def calling_subclass_method(self):
        for i in range(3):
            self.sub_class.subclass_method_1()
            self.sub_class.subclass_method_2()
            self.sub_class.subclass_method_3()

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

obj = Foo()
obj.example_method()
obj.calling_subclass_method()

profiler.stats()
```

output:
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!-- This file was created with the aha Ansi HTML Adapter. https://github.com/theZiz/aha -->
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="application/xml+xhtml; charset=UTF-8"/>
<title>stdin</title>
</head>
<body>
<pre>
Detailed Function Call Statistics:
<span style="color:#00ff00;"></span><span style="font-weight:bold;color:#00ff00;">Foo.__init__</span>: 2 calls, Total: 0.0001s, <span style="color:#00ff00;">Avg: 0.0000s</span>, Std: 0.0001s, Median: 0.0000s
<span style="color:#ff00ff;"></span><span style="font-weight:bold;color:#ff00ff;">Foo.example_method</span>: 1 calls, Total: 0.3003s, <span style="color:#ff00ff;">Avg: 0.3003s</span>
  └──<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Foo.another_method</span>:      1 calls, Total: 0.2001s, <span style="color:#ff0000;">Avg: 0.2001s</span>
<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Foo.calling_subclass_method</span>: 1 calls, Total: 0.3326s, <span style="color:#ff0000;">Avg: 0.3326s</span>
  ├──<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Bar.subclass_method_1</span>:  │   3 calls, Total: 0.1504s, <span style="color:#ff0000;">Avg: 0.0501s</span>, Std: 0.0001s, Median: 0.0501s
  ├──<span style="color:#ffafff;"></span><span style="font-weight:bold;color:#ffafff;">Bar.subclass_method_2</span>:  │   3 calls, Total: 0.0910s, <span style="color:#ffafff;">Avg: 0.0303s</span>, Std: 0.0001s, Median: 0.0303s
  │    ├──<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Bar.a</span>:       │   3 calls, Total: 0.0604s, <span style="color:#ff0000;">Avg: 0.0201s</span>, Std: 0.0001s, Median: 0.0201s
  │    └──<span style="color:#ffd7ff;"></span><span style="font-weight:bold;color:#ffd7ff;">Bar.b</span>:           3 calls, Total: 0.0303s, <span style="color:#ffd7ff;">Avg: 0.0101s</span>, Std: 0.0000s, Median: 0.0101s
  └──<span style="color:#ffafff;"></span><span style="font-weight:bold;color:#ffafff;">Bar.subclass_method_3</span>:      3 calls, Total: 0.0910s, <span style="color:#ffafff;">Avg: 0.0303s</span>, Std: 0.0002s, Median: 0.0303s
       ├──<span style="color:#ff0000;"></span><span style="font-weight:bold;color:#ff0000;">Bar.a</span>:       │   3 calls, Total: 0.0604s, <span style="color:#ff0000;">Avg: 0.0201s</span>, Std: 0.0001s, Median: 0.0201s
       └──<span style="color:#ffd7ff;"></span><span style="font-weight:bold;color:#ffd7ff;">Bar.b</span>:           3 calls, Total: 0.0304s, <span style="color:#ffd7ff;">Avg: 0.0101s</span>, Std: 0.0001s, Median: 0.0102s
</pre>
</body>
</html>


## Author
Arthur Bucker (<abucker@andrew.cmu.edu>)
