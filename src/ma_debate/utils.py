from __future__ import annotations
import json, os, random, hashlib
from datetime import datetime
from typing import Any, Optional

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def make_run_id(prefix: str = "run") -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    rand = hashlib.sha1(os.urandom(8)).hexdigest()[:6]
    return f"{prefix}-{ts}-{rand}"

def set_determinism(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(seed)

def jdump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
