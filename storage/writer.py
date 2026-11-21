import csv
import queue
import threading
from collections.abc import Iterable
from pathlib import Path

from core.models import Person
from utils.decorators import retry

# Domyślny folder na wygenerowane pliki (jest w .gitignore).
OUTPUT_DIR = Path("wyniki")


@retry(attempts=3, exceptions=(OSError,), delay=0.1)
def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=Person.FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_batches_parallel(
    batches: Iterable[list[dict[str, str]]],
    output_dir: Path = OUTPUT_DIR,
    workers: int = 4,
) -> list[Path]:
    if workers < 1:
        raise ValueError("workers musi wynosić co najmniej 1")

    jobs: queue.Queue = queue.Queue(maxsize=workers * 2)
    lock = threading.Lock()
    written: list[Path] = []
    errors: list[str] = []

    def worker() -> None:
        while True:
            job = jobs.get()
            if job is None:  # sygnał końca pracy
                return
            index, rows = job
            path = output_dir / f"osoby_{index:03d}.csv"
            try:
                write_csv(path, rows)
            except OSError as error:
                with lock:
                    errors.append(f"{path}: {error}")
            else:
                with lock:
                    written.append(path)

    threads = [
        threading.Thread(target=worker, name=f"writer-{number}")
        for number in range(workers)
    ]
    for thread in threads:
        thread.start()

    try:
        for index, batch in enumerate(batches, start=1):
            jobs.put((index, batch))
    finally:
        # Nawet gdy tworzenie paczek rzuci wyjątek, wątki muszą dostać sygnał
        for _ in threads:
            jobs.put(None)
        for thread in threads:
            thread.join()

    if errors:
        raise RuntimeError(f"Nie udało się zapisać {len(errors)} plików: {errors}")
    return sorted(written)