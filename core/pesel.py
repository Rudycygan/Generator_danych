from datetime import date

CENTURY_BY_MONTH_OFFSET = {
    80: 1800,
    0: 1900,
    20: 2000,
    40: 2100,
    60: 2200,
}

PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)


def decode_birth_date(date_part: str) -> date | None:
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
   
    total = sum(
        int(digit) * weight
        for digit, weight in zip(first_ten, PESEL_WEIGHTS, strict=True)
    )
    return (10 - total % 10) % 10


def valid_pesel(pesel):

    if not pesel.isdigit():
        return False

    if len(pesel) != 11:
        return False

    if decode_birth_date(pesel[0:6]) is None:
        return False

