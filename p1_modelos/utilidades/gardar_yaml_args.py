from pathlib import Path
from datetime import datetime, timezone

def gardar_yaml_args(path_yaml: Path, args_dict: dict, run_id: str) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    lines = [
        f'run_id: "{run_id}"',
        f'created_at_utc: "{created_at}"',
        'args:',
    ]
    for clave, valor in sorted(args_dict.items()):
        lines.append(f'  {clave}: {valor}')
    path_yaml.write_text('\n'.join(lines) + '\n', encoding='utf-8')
