from pathlib import Path
import csv

def append_rows_csv(path_csv: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path_csv.open('a', newline='', encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=rows[0].keys())
        writer.writerows(rows)
