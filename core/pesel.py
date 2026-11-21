"""Numer PESEL: odczyt daty urodzenia, cyfra kontrolna, walidacja i generowanie."""
import random
from datetime import date

# przypisanie na stałe liczby do danych stuleci z roku urodzenia. przy generowaniu zależnie od roku urodzenia do miesiąca doda się przypisana liczba
CENTURY_BY_MONTH_OFFSET = {
    80: 1800,
    0: 1900,
    20: 2000,
    40: 2100,
    60: 2200,
}
# wagi liczb w peselu, którymi później mnożymy cyfry w otrzymanym peselu w celu weryfikakcji
PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)

# liczba dodawana do miesiąca (używa go generator).
OFFSET_BY_CENTURY = {
    century: offset for offset, century in CENTURY_BY_MONTH_OFFSET.items()
}

# Dziesiąta cyfra numeru pesel: parzysta dla kobiet, nieparzysta dla mężczyzn.
SEX_DIGITS = {
    "K": (0, 2, 4, 6, 8),
    "M": (1, 3, 5, 7, 9),
}


def decode_birth_date(date_part: str) -> date | None:
    """odczytuje datę z numeru pesel i ją zwraca. W przypadku nie istniejącej daty zwraca None"""
    year_in_century = int(date_part[0:2])
    encoded_month = int(date_part[2:4])
    day = int(date_part[4:6])

    offset = encoded_month // 20 * 20
    century = CENTURY_BY_MONTH_OFFSET[offset]
    month = encoded_month - offset

    try:
        return date(century + year_in_century, month, day)
    except ValueError:
        return None


def calculate_check_digit(first_ten: str) -> int:
    """Oblicza cyfrę kontrolną. Robi to poprzez przemnożenie 10 pierwszych cyfr w numerze pesel, przez wagi do nich przypisane"""
    total = sum(
        int(digit) * weight
        for digit, weight in zip(first_ten, PESEL_WEIGHTS, strict=True)
    )
    return (10 - total % 10) % 10


def is_valid_pesel(pesel: str) -> bool:
    """waliduje podany numer pesel. Sprawdza przesłany format, długość numeru, datę urodzenia oraz zgodność cyfry kontrolnej"""
    # sprawdzenie, czy pesel w ogóle jest tekstem
    if not isinstance(pesel, str):
        return False
    #sprawdzenie, czy pesel to same cyfry
    if not pesel.isdigit() or not pesel.isascii():
        return False
    #sprawdzenie, czy pesel ma 11 znaków
    if len(pesel) != 11:
        return False
    #sprawdzenie, czy z pierwszych 6 cyfr wychodzi data urodzenia
    if decode_birth_date(pesel[0:6]) is None:
        return False
    expected = calculate_check_digit(pesel[:10])
    actual = int(pesel[-1])
    if expected != actual:
        return False
    return True


def generate_pesel(birth_date: date, sex: str) -> str:
    """Tworzy losowy, poprawny numer PESEL dla podanej daty urodzenia i płci
    Płeć podaje się jako "K" (kobieta) albo "M" (mężczyzna)
    Rzuca ValueError, gdy płeć jest nieznana albo rok urodzenia
    wypada poza zakres obsługiwany przez PESEL (1800-2299)
    """
    if sex not in SEX_DIGITS:
        raise ValueError(f"Nieznana płeć: {sex!r}, oczekiwano 'K' lub 'M'")

    century = birth_date.year // 100 * 100
    if century not in OFFSET_BY_CENTURY:
        raise ValueError(f"Rok {birth_date.year} poza zakresem 1800-2299")

    year_in_century = birth_date.year % 100
    encoded_month = birth_date.month + OFFSET_BY_CENTURY[century]
    serial = random.randint(0, 999)
    sex_digit = random.choice(SEX_DIGITS[sex])

    first_ten = (
        f"{year_in_century:02d}{encoded_month:02d}{birth_date.day:02d}"
        f"{serial:03d}{sex_digit}"
    )
    return first_ten + str(calculate_check_digit(first_ten))