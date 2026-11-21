"""Generatory i własny iterator do strumieniowego tworzenia fikcyjnych osób"""
from collections.abc import Iterable, Iterator

from core.models import Person


def generate_people(limit: int) -> Iterator[Person]:
    """Generuje `limit` losowych osób jedna po drugiej
    Rzuca TypeError, gdy limit nie jest liczbą całkowitą, i ValueError, gdy jest ujemny"""
    if not isinstance(limit, int):
        raise TypeError(f"limit musi być liczbą całkowitą, otrzymano {limit!r}")
    if limit < 0:
        raise ValueError("limit nie może być ujemny")
    for _ in range(limit):
        yield Person.random()


def filter_by_sex(people: Iterable[Person], sex: str) -> Iterator[Person]:
    """Przepuszcza dalej tylko osoby podanej płci "K" albo "M" """
    return (person for person in people if person.sex == sex)


def to_rows(people: Iterable[Person]) -> Iterator[dict[str, str]]:
    """Zamienia osoby na słowniki napisów gotowe do zapisu w CSV"""
    return (person.to_row() for person in people)


class Batches:
    """Własny iterator dzielący dowolny strumień elementów na paczki po `size` sztuk"""

    def __init__(self, items: Iterable, size: int) -> None:
        """Zapamiętuje iterator po elementach i rozmiar paczki (co najmniej 1)."""
        if size < 1:
            raise ValueError("size musi wynosić co najmniej 1")
        self._items = iter(items)
        self.size = size

    def __iter__(self) -> "Batches":
        """Zwraca sam obiekt, bo jest on jednocześnie iteratorem."""
        return self

    def __next__(self) -> list:
        """Zwraca kolejną paczkę albo rzuca StopIteration, gdy elementy się skończyły"""
        batch = []
        for item in self._items:
            batch.append(item)
            if len(batch) == self.size:
                break
        if not batch:
            raise StopIteration
        return batch
