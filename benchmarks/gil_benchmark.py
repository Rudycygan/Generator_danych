"""Benchmark GIL. Uruchomienie z katalogu projektu:  python -m benchmarks.gil_benchmark"""
import csv
import os
import time
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from core.generators import Batches, generate_people, to_rows
from core.parallel_validation import (
    count_valid_processes,
    count_valid_sequential,
    count_valid_threads,
    random_pesels,
)
from storage.writer import OUTPUT_DIR, write_batches_parallel
from utils.decorators import measure_time

CPU_SIZES = (100_000, 500_000, 1_000_000)  # ile numerów PESEL walidujemy
IO_FILES = 40                              # ile plików CSV zapisujemy
IO_ROWS_PER_FILE = 500                     # ile osób w jednym pliku
WORKERS = 4                                # liczba wątków / procesów
REPEATS = 3                                # ile powtórzeń; bierzemy najlepszy czas


def best_time(func: Callable, *args) -> float:
    """Uruchamia funkcję REPEATS zwraca najkrótszy czas w sekundach"""
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return min(times)


def benchmark_cpu() -> list[dict[str, object]]:
    """Mierzy zadanie obliczeniowe (CPU-bound): walidację numerów PESEL"""
    results = []
    for size in CPU_SIZES:
        pesels = list(random_pesels(size))
        sequential = best_time(count_valid_sequential, pesels)
        threads = best_time(count_valid_threads, pesels, WORKERS)
        processes = best_time(count_valid_processes, pesels, WORKERS)
        results.append({
            "zadanie": f"CPU: walidacja {size} PESEL",
            "sekwencyjnie_s": sequential,
            "watki_s": threads,
            "procesy_s": processes,
        })
    return results


def benchmark_io() -> dict[str, object]:
    """Mierzy zadanie wejścia-wyjścia (I/O-bound): zapis wielu plików CSV"""
    batches = list(Batches(to_rows(generate_people(IO_FILES * IO_ROWS_PER_FILE)),
                           IO_ROWS_PER_FILE))
    with TemporaryDirectory() as tmp:
        sequential = best_time(write_batches_parallel, batches, Path(tmp) / "seq", 1)
        threads = best_time(write_batches_parallel, batches, Path(tmp) / "thr", WORKERS)
    return {
        "zadanie": f"I/O: zapis {IO_FILES} plików CSV",
        "sekwencyjnie_s": sequential,
        "watki_s": threads,
        "procesy_s": None,
    }


def print_table(results: list[dict[str, object]]) -> None:
    """Wypisuje wyniki jako tabelę z przyspieszeniem względem wersji sekwencyjnej"""
    print(f"\n{'zadanie':<32}{'sekw. [s]':>11}{'wątki [s]':>11}{'procesy [s]':>13}"
          f"{'przysp. wątki':>15}{'przysp. procesy':>17}")
    for row in results:
        sequential = row["sekwencyjnie_s"]
        threads = row["watki_s"]
        processes = row["procesy_s"]
        processes_text = f"{processes:.3f}" if processes is not None else "-"
        speedup_processes = f"{sequential / processes:.2f}x" if processes else "-"
        print(f"{row['zadanie']:<32}{sequential:>11.3f}{threads:>11.3f}"
              f"{processes_text:>13}{sequential / threads:>14.2f}x{speedup_processes:>17}")


def save_results(results: list[dict[str, object]], path: Path) -> None:
    """Zapisuje wyniki benchmarku do pliku CSV"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


@measure_time
def main() -> None:
    """Uruchamia oba benchmarki, wypisuje tabelę i zapisuje wyniki"""
    print(f"Procesor: {os.cpu_count()} rdzeni logicznych, "
          f"{WORKERS} wątki/procesy, najlepszy z {REPEATS} pomiarów")
    results = benchmark_cpu()
    results.append(benchmark_io())
    print_table(results)
    save_results(results, OUTPUT_DIR / "benchmark.csv")
    print(f"\nWyniki zapisano w {OUTPUT_DIR / 'benchmark.csv'}")


if __name__ == "__main__":
    main()
