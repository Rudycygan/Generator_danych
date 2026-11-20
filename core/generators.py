from collections.abc import Iterable, Iterator

from core.models import Person


def generate_people(limit):
    count = 0
    while count < limit:
        yield Person.random()
        count += 1


def filter_by_sex(people: Iterable[Person], sex: str) -> Iterator[Person]:
    return (person for person in people if person.sex == sex)


def to_rows(people: Iterable[Person]) -> Iterator[dict[str, str]]:
    return (person.to_row() for person in people)