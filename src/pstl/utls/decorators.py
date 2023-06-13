

import inspect

import numpy as np


def add_empty_dict(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result, {}
    return wrapper


def absorb_extra_args_kwargs_old(func):
    def wrapper(*args, **kwargs):
        print("Before the function is executed.")
        # absorb any extra arguments and keyword arguments here
        extra_args = [
            arg for arg in args if arg not in func.__code__.co_varnames]
        extra_kwargs = {key: val for key, val in kwargs.items(
        ) if key not in func.__code__.co_varnames}
        result = func(*args, **kwargs)
        print("After the function is executed.")
        return result
    return wrapper


def absorb_extra_args_kwargs(func):
    def wrapper(*args, **kwargs):
        # Separate the defined args and kwargs from the extra ones
        defined_args = args[:func.__code__.co_argcount]
        defined_kwargs = {
            k: v for k, v in kwargs.items() if k in func.__code__.co_varnames}

        extra_args = args[func.__code__.co_argcount:]
        extra_kwargs = {k: v for k, v in kwargs.items(
        ) if k not in func.__code__.co_varnames}

        # Call the decorated function with the defined args and kwargs
        result = func(*defined_args, **defined_kwargs)

        # Output a message indicating that the function has been executed
        # print(f"{func.__name__} has been executed")

        return result

    return wrapper


def where_function_else_zero(func, condition_func):

    def wrapper(*args, **kwargs):
        condition = condition_func(*args, **kwargs)
        return np.where(condition, func(*args, **kwargs), 0)
    return wrapper


def dict_args(func):
    sig = inspect.signature(func)
    arg_names = tuple(sig.parameters.keys())

    def wrapper(args_dict):
        args = tuple(args_dict.get(name, inspect.Parameter.empty)
                     for name in arg_names)
        return func(*args)

    return wrapper
