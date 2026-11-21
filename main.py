"""Generator i walidator danych testowych - punkt wejścia programu"""
import argparse
import sys
from pathlib import Path

from core.generators import Batches, filter_by_sex, generate_people, to_rows
from core.patterns import validate_row
from storage.writer import OUTPUT_DIR, read_csv, write_batches_parallel
from utils.decorators import measure_time


def positive_int(text: str) -> int:
    """Typ argumentu dla argparse: liczba całkowita większa od zera"""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"to nie jest liczba całkowita: {text!r}")
    if value < 1:
        raise argparse.ArgumentTypeError(f"wartość musi być większa od 0: {value}")
    return value


@measure_time
def run_generate(args: argparse.Namespace) -> int:
    """generuje osoby i zapisuje je w paczkach do plików CSV"""
    people = generate_people(args.count)
    if args.sex is not None:
        people = filter_by_sex(people, args.sex)
    batches = Batches(to_rows(people), args.batch)
    files = write_batches_parallel(batches, args.output, args.workers)
    print(f"Zapisano {len(files)} plików w folderze {args.output}")
    return 0


def collect_csv_files(paths: list[Path]) -> list[Path]:
    """Zamienia podane ścieżki na listę plików CSV"""
    files = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.csv")))
        elif path.is_file():
            files.append(path)
        else:
            print(f"Pominięto: {path} nie istnieje")
    return files


@measure_time
def run_validate(args: argparse.Namespace) -> int:
    """sprawdza wiersze w plikach CSV i wypisuje błędy"""
    files = collect_csv_files(args.paths)
    if not files:
        print("Nie znaleziono żadnych plików CSV")
        return 1
    total_rows = 0
    bad_rows = 0
    for file in files:
        for line_number, row in enumerate(read_csv(file), start=2):  # linia 1 to nagłówek
            total_rows += 1
            errors = validate_row(row)
            if errors:
                bad_rows += 1
                print(f"{file}:{line_number}: {'; '.join(errors)}")
    print(f"Sprawdzono {total_rows} wierszy w {len(files)} plikach, błędnych: {bad_rows}")
    return 1 if bad_rows else 0


def run_benchmark(args: argparse.Namespace) -> int:
    """uruchamia benchmark GIL"""
    from benchmarks.gil_benchmark import main as benchmark_main
    benchmark_main()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Buduje parser argumentów z trzema podkomendami: generate, validate, benchmark"""
    parser = argparse.ArgumentParser(description="Generator i walidator danych testowych")
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="wygeneruj osoby do plików CSV")
    generate.add_argument("--count", type=positive_int, default=1000,
                          help="ile osób wygenerować (domyślnie 1000)")
    generate.add_argument("--batch", type=positive_int, default=250,
                          help="ile osób w jednym pliku (domyślnie 250)")
    generate.add_argument("--workers", type=positive_int, default=4,
                          help="liczba wątków zapisujących (domyślnie 4)")
    generate.add_argument("--sex", choices=("K", "M"),
                          help="zostaw tylko osoby tej płci (plików będzie mniej)")
    generate.add_argument("--output", type=Path, default=OUTPUT_DIR,
                          help=f"folder na pliki (domyślnie {OUTPUT_DIR})")
    generate.set_defaults(handler=run_generate)

    validate = commands.add_parser("validate", help="sprawdź poprawność plików CSV")
    validate.add_argument("paths", type=Path, nargs="+",
                          help="pliki CSV albo foldery z plikami CSV")
    validate.set_defaults(handler=run_validate)

    benchmark = commands.add_parser("benchmark", help="uruchom benchmark GIL")
    benchmark.set_defaults(handler=run_benchmark)

    return parser


def main() -> int:
    """Czyta argumenty, uruchamia wybraną podkomendę i zwraca kod wyjścia programu."""
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, RuntimeError) as error:
        print(f"Błąd: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
