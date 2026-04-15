from pathlib import Path
import hashlib
import time

def crear_run_dir(base_dir: Path):
    base_dir.mkdir(parents=True, exist_ok=True)
    run_id = hashlib.sha1(str(time.time_ns()).encode('utf-8')).hexdigest()[:6]
    run_dir = base_dir / run_id
    if not run_dir.exists():
        run_dir.mkdir(parents=True)
        return run_id, run_dir
