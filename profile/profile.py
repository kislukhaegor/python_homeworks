from time import time
from functools import wraps
from inspect import isclass

def __profile_func(obj):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"`{f.__name__}` started")
        timer = time()
        ret_value = f(*args, **kwargs)
        print(f"`{f.__name__}` finished in {time() - timer:.2f}s")
        return ret_value
    return wrapper

def __profile_class_method(cls):
        def impl(cls_method):
            @wraps(cls_method)
            def wrapper(*args, **kwargs):
                print(f"`{cls.__name__}.{cls_method.__name__}` started")
                timer = time()
                ret_value = cls_method(*args, **kwargs)
                print(f"`{cls.__name__}.{cls_method.__name__}` finished in {time() - timer:.2f}s")
                return ret_value
            return wrapper
        return impl

def profile(obj):
    if isclass(obj):
        for attr_name in obj.__dict__:
            attr = getattr(obj, attr_name)
            if callable(attr):
                setattr(obj, attr_name, __profile_class_method(obj)(attr))
        return obj
    print(obj)
    return __profile_func(obj)