"""Wyrażenia regularne z grupami nazwanymi oraz walidacja wierszy z danymi osób"""
import re

from core.pesel import is_valid_pesel

# PESEL: 11 cyfr podzielonych na nazwane części.
PESEL_PATTERN = re.compile(
    r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})"
    r"(?P<serial>\d{3})(?P<sex>\d)(?P<check>\d)",
    re.ASCII,
)

# E-mail: login@domena.końcówka
EMAIL_PATTERN = re.compile(
    r"(?P<login>[a-z0-9._-]+)@(?P<domain>[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,})",
    re.ASCII | re.IGNORECASE,
)

# Telefon komórkowy: opcjonalne +48, potem 9 cyfr zaczynających się od 5-8.
PHONE_PATTERN = re.compile(r"(?:\+48)?(?P<number>[5-8]\d{8})", re.ASCII)

# Kod pocztowy: dwie cyfry, myślnik, trzy cyfry, np. 00-950.
POSTAL_CODE_PATTERN = re.compile(r"(?P<region>\d{2})-(?P<office>\d{3})", re.ASCII)


def parse_pesel(pesel: str) -> dict[str, str] | None:
    """Rozbija PESEL na nazwane części: year, month, day, serial, sex, check"""
    match = PESEL_PATTERN.fullmatch(pesel)
    if match is None:
        return None
    return match.groupdict()


def email_domain(email: str) -> str | None:
    """Zwraca domenę adresu e-mail albo None, gdy adres jest niepoprawny"""
    match = EMAIL_PATTERN.fullmatch(email)
    if match is None:
        return None
    return match.group("domain")


def validate_row(row: dict[str, str]) -> list[str]:
    """Sprawdza wiersz danych osoby (np. wczytany z CSV): PESEL, e-mail, telefon, kod.
       Zwraca listę opisów wszystkich znalezionych błędów"""
    errors = []
    # "or ''" zamienia zarówno brak klucza, jak i None (krótki wiersz CSV) na pusty napis.
    if not is_valid_pesel(row.get("pesel") or ""):
        errors.append(f"niepoprawny PESEL: {row.get('pesel')!r}")
    if EMAIL_PATTERN.fullmatch(row.get("email") or "") is None:
        errors.append(f"niepoprawny e-mail: {row.get('email')!r}")
    if PHONE_PATTERN.fullmatch(row.get("phone") or "") is None:
        errors.append(f"niepoprawny telefon: {row.get('phone')!r}")
    if POSTAL_CODE_PATTERN.fullmatch(row.get("postal_code") or "") is None:
        errors.append(f"niepoprawny kod pocztowy: {row.get('postal_code')!r}")
    return errors
