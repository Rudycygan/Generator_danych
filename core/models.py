import functools
import random
from collections.abc import Callable
from datetime import date, timedelta

from core.pesel import SEX_DIGITS, decode_birth_date, generate_pesel, is_valid_pesel
from core.sample_data import EMAIL_DOMAINS, FIRST_NAMES, LAST_NAMES

# Zakres dat urodzenia losowanych osób.
MIN_BIRTH_DATE = date(1940, 1, 1)
MAX_BIRTH_DATE = date(2007, 12, 31)

# Zamiana polskich znaków na ich odpowiedniki ASCII (do adresów e-mail).
POLISH_TO_ASCII = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")


def requires_consistency(method: Callable) -> Callable:
    """Dekorator metody: przed jej wywołaniem sprawdza spójność obiektu.
    wyrzuca ValueError, gdy PESEL osoby nie zgadza się
    z jej datą urodzenia albo płcią.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_consistent():
            raise ValueError(f"Niespójne dane osoby: {self!r}")
        return method(self, *args, **kwargs)

    return wrapper


class Person:
    """Fikcyjna osoba: dane osobowe i kontaktowe."""

    # Kolejność kolumn przy zapisie do CSV.
    FIELDS = (
        "first_name", "last_name", "sex", "birth_date",
        "pesel", "email", "phone", "postal_code",
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        sex: str,
        birth_date: date,
        pesel: str,
        email: str,
        phone: str,
        postal_code: str,
    ) -> None:
        if sex not in SEX_DIGITS:
            raise ValueError(f"Nieznana płeć: {sex!r}, oczekiwano 'K' lub 'M'")
        self.first_name = first_name
        self.last_name = last_name
        self.sex = sex
        self.birth_date = birth_date
        self.pesel = pesel  # wywołuje setter, który waliduje numer
        self.email = email
        self.phone = phone
        self.postal_code = postal_code

    @property
    def pesel(self) -> str:
        """Numer PESEL osoby"""
        return self._pesel

    @pesel.setter
    def pesel(self, value: str) -> None:
        if not is_valid_pesel(value):
            raise ValueError(f"Niepoprawny PESEL: {value!r}")
        self._pesel = value

    def __repr__(self) -> str:
        return (f"Person({self.first_name} {self.last_name}, "
                f"{self.sex}, {self.birth_date}, PESEL {self.pesel})")

    def is_consistent(self) -> bool:
        """Sprawdza, czy PESEL pasuje do daty urodzenia i płci osoby"""
        sex_digit = int(self.pesel[9])
        return (decode_birth_date(self.pesel[:6]) == self.birth_date
                and sex_digit in SEX_DIGITS[self.sex])

    @requires_consistency
    def to_row(self) -> dict[str, str]:
        """Zwraca dane osoby jako słownik napisów, gotowy do zapisu w CSV."""
        row = {field: str(getattr(self, field)) for field in self.FIELDS}
        row["birth_date"] = self.birth_date.isoformat()
        return row

    @staticmethod
    def make_email(first_name: str, last_name: str) -> str:
        """Tworzy adres e-mail z imienia i nazwiska"""
        login = f"{first_name}.{last_name}".translate(POLISH_TO_ASCII).lower()
        return f"{login}{random.randint(1, 99)}@{random.choice(EMAIL_DOMAINS)}"

    @classmethod
    def random(cls) -> "Person":
        """Tworzy losową, spójną osobę"""
        sex = random.choice(tuple(SEX_DIGITS))
        first_name = random.choice(FIRST_NAMES[sex])
        last_name = random.choice(LAST_NAMES[sex])
        days_range = (MAX_BIRTH_DATE - MIN_BIRTH_DATE).days
        birth_date = MIN_BIRTH_DATE + timedelta(days=random.randint(0, days_range))
        return cls(
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            birth_date=birth_date,
            pesel=generate_pesel(birth_date, sex),
            email=cls.make_email(first_name, last_name),
            phone=f"{random.choice('5678')}{random.randint(0, 99_999_999):08d}",
            postal_code=f"{random.randint(0, 99):02d}-{random.randint(0, 999):03d}",
        )

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Person":
        """Odtwarza osobę ze słownika wczytanego z pliku CSV"""
        data = dict(row)
        data["birth_date"] = date.fromisoformat(row["birth_date"])
        return cls(**data)
