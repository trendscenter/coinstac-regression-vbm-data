#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:48:19 2019

@author: hgazula
"""

try:
    from line_profiler import LineProfiler

    def do_profile(follow=[]):
        def inner(func):
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)
                    for f in follow:
                        profiler.add_function(f)
                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    with open('time_stats', 'w') as fp:
                        profiler.print_stats(stream=fp, output_unit=1)
            return profiled_func
        return inner

except ImportError:
    def do_profile(follow=[]):
        "Helpful if you accidentally leave in production!"
        def inner(func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return inner

@do_profile(follow=[])
def get_number():
    for x in range(5000000):
        yield x

def expensive_function():
    for x in get_number():
        i = x ^ x ^ x
    return 'some result!'

result = expensive_function()