from datetime import date

#przypisanie na stałe liczby do danych stuleci z roku urodzenia. zależnie od roku urodzenia do miesiąca doda się przypisana liczba
CENTURY_BY_MONTH_OFFSET = {
    80: 1800,
    0: 1900,
    20: 2000,
    40: 2100,
    60: 2200,
}
# wagi liczb w peselu, którymi później mnożymy cyfry w otrzymanym peselu w celu weryfikakcji
PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)


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
