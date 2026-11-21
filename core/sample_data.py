"""Dane, z których losowane są fikcyjne osoby: imiona, nazwiska i domeny e-mail."""

FIRST_NAMES = {
    "K": (
        "Anna", "Maria", "Katarzyna", "Małgorzata", "Agnieszka", "Barbara",
        "Ewa", "Krystyna", "Magdalena", "Joanna", "Zofia", "Julia", "Łucja",
    ),
    "M": (
        "Piotr", "Krzysztof", "Andrzej", "Tomasz", "Paweł", "Jan", "Michał",
        "Marcin", "Jakub", "Adam", "Łukasz", "Mateusz", "Stanisław",
    ),
}

# Nazwiska w formie żeńskiej i męskiej.
LAST_NAMES = {
    "K": (
        "Nowak", "Kowalska", "Wiśniewska", "Wójcik", "Kowalczyk",
        "Kamińska", "Lewandowska", "Zielińska", "Szymańska", "Woźniak",
        "Dąbrowska", "Kozłowska", "Jankowska", "Mazur", "Krawczyk",
    ),
    "M": (
        "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk",
        "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak",
        "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Krawczyk",
    ),
}

EMAIL_DOMAINS = ("example.com", "example.org", "example.net")
