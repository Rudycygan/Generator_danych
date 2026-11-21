"""Dekoratory funkcji używane w całym projekcie: pomiar czasu i ponawianie prób"""
import functools
import time
from collections.abc import Callable


def measure_time(func: Callable) -> Callable:
    """Wypisuje, ile sekund trwało wykonanie udekorowanej funkcji."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] wykonano w {elapsed:.4f} s")
        return result

    return wrapper


def retry(
    attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    delay: float = 0.0,
) -> Callable:
    """Ponawia wywołanie funkcji, gdy rzuci jeden z podanych wyjątków.
    attempts - ile razy maksymalnie wywołać funkcję (co najmniej 1),
    exceptions - wyjątki, po których warto spróbować ponownie,
    delay - przerwa w sekundach między próbami"""
    if attempts < 1:
        raise ValueError("attempts musi wynosić co najmniej 1")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    print(f"[{func.__name__}] próba {attempt}/{attempts} "
                          f"nieudana: {error}")
                    if attempt == attempts:
                        raise
                    time.sleep(delay)

        return wrapper

    return decorator
