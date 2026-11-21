import random
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import date, timedelta

from core.pesel import generate_pesel, is_valid_pesel

FIRST_DAY = date(1900, 1, 1)
DAYS_RANGE = (date(2099, 12, 31) - FIRST_DAY).days


def random_pesels(count: int, invalid_ratio: float = 0.1) -> Iterator[str]:
    for _ in range(count):
        birth_date = FIRST_DAY + timedelta(days=random.randint(0, DAYS_RANGE))
        pesel = generate_pesel(birth_date, random.choice("KM"))
        if random.random() < invalid_ratio:
            wrong_digit = (int(pesel[-1]) + 1) % 10
            pesel = pesel[:-1] + str(wrong_digit)
        yield pesel


def split_into_chunks(items: list[str], parts: int) -> list[list[str]]:
    if parts < 1:
        raise ValueError("parts musi wynosić co najmniej 1")
    size = max(1, -(-len(items) // parts))  # dzielenie z zaokrągleniem w górę
    return [items[start:start + size] for start in range(0, len(items), size)]


def count_valid(pesels: list[str]) -> int:
    return sum(1 for pesel in pesels if is_valid_pesel(pesel))


def count_valid_sequential(pesels: list[str]) -> int:
    return count_valid(pesels)


def count_valid_threads(pesels: list[str], workers: int = 4) -> int:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return sum(executor.map(count_valid, split_into_chunks(pesels, workers)))


def count_valid_processes(pesels: list[str], workers: int = 4) -> int:
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return sum(executor.map(count_valid, split_into_chunks(pesels, workers)))


if __name__ == "__main__":
    sample = list(random_pesels(200_000))
    print("sekwencyjnie:", count_valid_sequential(sample))
    print("wątki:       ", count_valid_threads(sample))
    print("procesy:     ", count_valid_processes(sample))
