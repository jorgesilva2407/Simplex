import time
import functools

@functools.wraps(print)
def print(*args, **kwargs):
    # Your custom print logic here
    # For example, you can add a timestamp to the output
    print_time = time.time()
    __builtins__.print(f"[{print_time}] ", end="")
    return __builtins__.print(*args, **kwargs)

print('anything')