# Generator i walidator danych testowych (temat 10)

Program robi dwie rzeczy: generuje fikcyjne dane osobowe i zapisuje je w paczkach do plików CSV, a potem potrafi takie pliki sprawdzić. Dane są spójne, czyli PESEL pasuje do daty urodzenia i płci (cyfra parzysta/nieparzysta), a imię i nazwisko są dobrane do płci. Walidator sprawdza PESEL (format, czy data istnieje w kalendarzu, suma kontrolna) oraz format maila, telefonu i kodu pocztowego.

Do tego doszedł mały benchmark, w którym porównuję wykonanie sekwencyjne, na wątkach i na procesach, żeby zobaczyć w praktyce, jak działa GIL.

## Wymagania i uruchamianie

Potrzebny jest Python 3.12 lub nowszy (pisałem na 3.13.4). Żadnych zewnętrznych bibliotek nie trzeba, używam tylko biblioteki standardowej.

Komendy odpala się z głównego katalogu projektu:

```bash
# lista komend i flag
python main.py --help

# 5000 osób, po 1000 w pliku (domyślnie ląduje w folderze wyniki/)
python main.py generate --count 5000 --batch 1000

# same kobiety, zapis na 8 wątkach, własny katalog
python main.py generate --count 2000 --sex K --workers 8 --output wyniki/kobiety

# walidacja wszystkich CSV w katalogu (może być też pojedynczy plik)
python main.py validate wyniki

# benchmark, trwa około minuty
python main.py benchmark
```

Uwaga dla PyCharma: jeśli odpalisz `main.py` zieloną strzałką bez parametrów, wypisze się tylko pomoc z `argparse`, bo program wymaga podkomendy (`generate`, `validate` albo `benchmark`). Parametry trzeba wpisać w Run -> Edit Configurations -> Script parameters.

### Flagi `generate`

| Flaga | Opis | Domyślnie |
|---|---|---|
| `--count` | ile osób wygenerować łącznie | `1000` |
| `--batch` | ile rekordów w jednym pliku CSV | `250` |
| `--workers` | ile wątków zapisuje pliki | `4` |
| `--sex` | filtr płci (`K` albo `M`), bez flagi są obie | brak |
| `--output` | katalog wyjściowy | `wyniki` |

### Kody wyjścia
- `generate` zwraca `0`, gdy wszystko się zapisze, i `1` przy błędzie I/O.
- `validate` zwraca `0`, gdy pliki są poprawne, i `1`, gdy znajdzie błędy. Błędy wypisuje w formacie `plik:numer_linii: opis`.

## Struktura projektu

```text
Generator_danych/
├── main.py                      # argparse i spięcie całości
├── core/
│   ├── pesel.py                 # data z PESEL-u, suma kontrolna, generator i walidator
│   ├── sample_data.py           # listy imion, nazwisk i domen
│   ├── models.py                # klasa Person i dekorator pilnujący spójności danych
│   ├── generators.py            # generatory osób i iterator Batches
│   ├── patterns.py              # regexy z grupami nazwanymi, walidacja wiersza CSV
│   └── parallel_validation.py   # walidacja PESEL-i na wątkach i procesach
├── storage/
│   └── writer.py                # CSV oraz kolejka producent-konsument (Queue + Lock)
├── utils/
│   └── decorators.py            # measure_time i retry
└── benchmarks/
    └── gil_benchmark.py         # pomiary wydajności
```

Cały potok jest leniwy:
`generate_people` -> `filter_by_sex` -> `to_rows` -> `Batches` -> `write_batches_parallel`

Kolejka między generatorem a wątkami zapisującymi ma ograniczony rozmiar. Dzięki temu nie trzymam w pamięci milionów rekordów naraz, a nowa paczka powstaje dopiero wtedy, gdy któryś wątek zwolni miejsce.

## Gdzie co jest

Dekoratory (`utils/decorators.py`, `core/models.py`):
- `measure_time` (z `functools.wraps`) mierzy czas komend i testów w benchmarku.
- `retry(attempts, exceptions, delay)` to dekorator z parametrami, nałożony na `write_csv`. Przy chwilowym `OSError` ponawia zapis.
- `requires_consistency` to dekorator metody (używa `self`). W `Person.to_row()` sprawdza, czy PESEL nadal zgadza się z płcią i datą urodzenia.

Klasa `Person` (`core/models.py`):
- `@property` i setter dla pola `pesel`, który od razu waliduje wpisywany numer.
- `@classmethod`: `Person.random()` i `Person.from_row()`.
- `@staticmethod`: `Person.make_email()`.

Iteratory i generatory:
- Własny iterator `Batches` (`__iter__`, `__next__`) dzieli strumień na paczki o zadanym rozmiarze.
- Funkcje z `yield`: `generate_people` i `random_pesels`.
- Wyrażenia generujące: `filter_by_sex`, `to_rows`, `calculate_check_digit`, `count_valid`.

Regexy (`core/patterns.py`): `PESEL_PATTERN`, `EMAIL_PATTERN`, `PHONE_PATTERN`, `POSTAL_CODE_PATTERN`, wszystkie z grupami nazwanymi. Korzystam z nich m.in. w `parse_pesel` (przez `groupdict()`) i w `email_domain`.

Współbieżność:
- Zapis CSV to producent-konsument na wątkach z `queue.Queue` i `threading.Lock` (`storage/writer.py`).
- Walidacja, która mocno obciąża procesor, idzie przez `ProcessPoolExecutor` w `count_valid_processes`.

## Benchmark i GIL

Mierzyłem na Windows 11, procesor 12-wątkowy, Python 3.13.4. Wersje równoległe dostały po 4 wątki albo 4 procesy. W tabeli jest najlepszy czas z 3 podejść (wyniki zapisują się też do `wyniki/benchmark.csv`).

| Zadanie | Sekwencyjnie [s] | Wątki [s] | Procesy [s] | Przysp. wątki | Przysp. procesy |
|---|---:|---:|---:|---:|---:|
| CPU: walidacja 100 000 PESEL | 0,300 | 0,302 | 0,223 | 0,99x | 1,34x |
| CPU: walidacja 500 000 PESEL | 1,508 | 1,512 | 0,609 | 1,00x | 2,48x |
| CPU: walidacja 1 000 000 PESEL | 3,024 | 3,032 | 1,063 | 1,00x | 2,84x |
| I/O: zapis 40 plików CSV (po 500 osób) | 0,094 | 0,083 | - | 1,14x | - |

Wnioski:
- Wątki nic nie dały przy liczeniu. Walidacja PESEL-i na 4 wątkach trwała tyle samo co na jednym, a czasem odrobinę dłużej. To właśnie GIL: w danej chwili bajtkod Pythona wykonuje tylko jeden wątek, więc reszta rdzeni się nudzi.
- Procesy omijają GIL, ale kosztują. Przy milionie PESEL-i 4 procesy dały 2,84x, a nie 4x. Zakładam, że to wina narzutu: Windows startuje procesy metodą spawn (nowy interpreter) i dane idą przez `pickle`. Przy 100 tys. numerów ten narzut zjada większość zysku (1,34x). Dlatego dzielę dane na duże kawałki (`split_into_chunks`), a nie wysyłam pojedynczych numerów.
- Przy zapisie plików wątki pomogły tylko trochę (1,14x). Podczas operacji na dysku wątek zwalnia GIL, ale pliki są małe, a system i tak buforuje je w pamięci, więc czekania prawie nie ma. Sporo czasu zajmuje też zwykłe składanie stringów w Pythonie, a to GIL trzyma.

## Co poszło nie tak podczas pisania

- Kolizja nazwy `io`. Pakiet do plików nazwałem na początku `io` i tym samym przykryłem moduł z biblioteki standardowej, przez co import się sypał. Zmieniłem nazwę na `storage`.
- Zawieszanie przy błędzie. W pierwszej wersji zapisu wielowątkowego, gdy generator rzucił wyjątek w trakcie, wątki robocze nie dostawały `None` jako sygnału końca i program wisiał. Naprawiłem to, wrzucając wysyłanie `None` do `finally`.
- `None` w niepełnych wierszach. Gdy w testowym pliku brakowało kolumn na końcu linii, `csv.DictReader` wstawiał `None` zamiast pustego stringa. `row.get("email", "")` nie pomagało, bo klucz istniał, i regex wywalał `TypeError`. Zadziałało dopiero `row.get("email") or ""`.
- Ciche błędy w wątkach. Gdy do `DictWriter` trafił wiersz z nadmiarową kolumną, wątek rzucał `ValueError` i po prostu kończył działanie bez słowa. Teraz łapię `ValueError` razem z `OSError`, zbieram błędy ze wszystkich wątków do jednej listy, a główny wątek na końcu rzuca z niej `RuntimeError`.
- `pickle` i procesy na Windowsie. Spawn wymusił, żeby start `ProcessPoolExecutor` siedział pod `if __name__ == "__main__":` i żeby `count_valid` była zdefiniowana na poziomie modułu, bo inaczej nie da się jej zserializować.
