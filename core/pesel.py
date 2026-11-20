from datetime import date

CENTURY_BY_MONTH_OFFSET = {
    80: 1800,
    0: 1900,
    20: 2000,
    40: 2100,
    60: 2200,
}


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

def valid_pesel(pesel):

    if not pesel.isdigit():
        return False

    if decode_birth_date(pesel[0:6]) is None:
        return False
