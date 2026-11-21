from collections.abc import Iterable, Iterator

from core.models import Person


def generate_people(limit: int) -> Iterator[Person]:
    if not isinstance(limit, int):
        raise TypeError(f"limit musi być liczbą całkowitą, otrzymano {limit!r}")
    if limit < 0:
        raise ValueError("limit nie może być ujemny")
    for _ in range(limit):
        yield Person.random()


def filter_by_sex(people: Iterable[Person], sex: str) -> Iterator[Person]:
    return (person for person in people if person.sex == sex)


def to_rows(people: Iterable[Person]) -> Iterator[dict[str, str]]:
    return (person.to_row() for person in people)


class Batches:

    def __init__(self, items: Iterable, size: int) -> None:
        if size < 1:
            raise ValueError("size musi wynosić co najmniej 1")
        self._items = iter(items)
        self.size = size

    def __iter__(self) -> "Batches":
        return self

    def __next__(self) -> list:
        batch = []
        for item in self._items:
            batch.append(item)
            if len(batch) == self.size:
                break
        if not batch:
            raise StopIteration
        return batch
