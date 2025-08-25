
from flexprofiler import track, track_all, stats
import time

# Simple Example: Track a single function with arg_sensitive
@track(arg_sensitive=["foo"])
def foo(x):
    time.sleep(0.05 * x)
    return x * 2

foo(1)
foo(2)
foo(1)
foo(3)

print("Simple Example Stats:")
stats()

# Complex Example: Track methods in a class with arg_sensitive
@track_all(arg_sensitive=["bar", "baz"])
class MyClass:
    def bar(self, a):
        time.sleep(0.01 * a)
        return a + 1
    def baz(self, b, c=0):
        time.sleep(0.02 * b + 0.01 * c)
        return b * c
    def run(self):
        for i in range(3):
            self.bar(i)
            self.baz(i, c=i+1)
            self.baz(i, c=0)

obj = MyClass()
obj.run()
obj.bar(2)
obj.baz(2, c=5)

print("\nComplex Example Stats:")
stats()
