from time import time
from functools import wraps
from inspect import isclass

def __profile_impl(cls):
    def impl(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if cls:
                f_str = f"`{cls.__name__}.{func.__name__}`"
            else:
                f_str = f"`{func.__name__}`"
            
            print(f"{f_str} started")
            timer = time()
            ret_value = func(*args, **kwargs)
            print(f"{f_str} finished in {time() - timer:.2f}s")
            return ret_value
        return wrapper
    return impl

def profile(obj):
    if isclass(obj):
        for attr_name in obj.__dict__:
            attr = getattr(obj, attr_name)
            if callable(attr):
                setattr(obj, attr_name, __profile_impl(obj)(attr))
        return obj
    return __profile_impl(None)(obj)