from functools import wraps, partial

def log(func=None, /, *, prefix='###'):
    if func is None:
        return partial(log, prefix=prefix)

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'{prefix} Calling {func.__qualname__} with', args, kwargs)
        result = func(*args, **kwargs)
        print(f'{prefix} {func.__qualname__} returned {result}')
        return result
    return wrapper


def log_methods(cls):
    for name, value in vars(cls).items():
        if callable(value):
            print(name)
            setattr(cls, name, log(value))
    return cls


@log_methods    
class Maths:
    @staticmethod
    def add(x, y):
        return x + y

    @staticmethod
    def sub(x, y):
        return  x - y
