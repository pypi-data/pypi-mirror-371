from __future__ import annotations
from pathlib import Path
import json, time
from typing import Optional, Dict, Any

def emit(telemetry_dir: Optional[str], run_id: Optional[str], rec: Dict[str, Any]):
    if not telemetry_dir or not run_id:
        return
    p = Path(telemetry_dir) / f"{run_id}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = dict({"ts": time.time()}, **rec)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
