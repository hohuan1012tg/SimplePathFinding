import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def timed(*args, **kwargs):
        timestart = time.time()
        result = func(*args, **kwargs)
        timeend = time.time()

        timed.time_elapsed = float((timeend - timestart) * 1000)
        print("{} runs in  {:.2f} milliseconds".format(func.__name__, (timeend - timestart) * 1000))
        
        return result
    return timed