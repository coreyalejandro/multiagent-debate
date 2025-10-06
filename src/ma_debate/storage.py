from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

class JSONLRunLogger:
    def __init__(self, output_dir: str = "runs", run_id: str | None = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.output_dir / f"{run_id or 'run'}.jsonl"
        self._fp = open(self.path, "a", encoding="utf-8")

    def log(self, record: Dict[str, Any]) -> None:
        self._fp.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fp.flush()

    def close(self) -> None:
        try:
            self._fp.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
