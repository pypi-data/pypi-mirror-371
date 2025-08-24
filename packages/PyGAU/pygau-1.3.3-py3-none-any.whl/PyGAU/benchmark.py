"""
Classes and functions meant to benchmark your code
"""

import time as _time

class Timing:

    """
    Time whatever program you want!
    More easy than "Timeit"!

    Only use the decorator "dcount" to measure performance

    you can instantiate the class to make get acces to more methods!
    (like start_count and stop_count)
    """

    def __init__(self):

        self.start_time = 0
        self.ns = False

    def start_count(self, ns=False):

        """
        Start a counter to see how many time consumes a func!
        """
        
        self.ns = ns

        if self.ns:

            self.start_time = _time.perf_counter_ns()

        else:

            self.start_time = _time.perf_counter()


    def stop_count(self):

        """
        Stop the counter and see how many time took to execute!

        NOTE: if the counter was not started the result would be a negative number or 0.
        """

        if self.ns:

            finish_time = _time.perf_counter_ns()
            print("Time taken", finish_time - self.start_time, "ns")

        else:

            finish_time = _time.perf_counter()
            print("Time taken", finish_time - self.start_time, "s")

    def dcount(repeats=1, ns=False):

        """
        Count the performance of every program easily
        only select how many repeats to take the median and wait!
        ns means if the result is show in seconds or nanoseconds (for fast programs)
        """

        def decorator(func):

            def modification(*args, **kwargs):

                if ns:

                    start_time = _time.perf_counter_ns()

                else:

                    start_time = _time.perf_counter()

                for repeat in range(repeats):

                    bullshit = func(*args, **kwargs)

                if ns:

                    final_time = _time.perf_counter_ns()
                    char_val = "ns"

                else:

                    final_time = _time.perf_counter()
                    char_val = "s"

                
 
                print("Mid time taken in", repeats, "iterations by the function", func.__name__ + str(":"), (final_time - start_time)/repeats, char_val)

                return ((final_time - start_time)/repeats, bullshit)

            return modification

        return decorator