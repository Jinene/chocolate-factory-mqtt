from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict
import random

def utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class BatchContext:
    product_type: str
    batch_id: str

def make_batch_id(product_type: str) -> str:
    # Example: B20260111-DA-0042
    code = {"white": "WH", "milk": "MI", "dark": "DA"}[product_type]
    ymd = datetime.now().strftime("%Y%m%d")
    seq = random.randint(1, 9999)
    return f"B{ymd}-{code}-{seq:04d}"

def telemetry_payload(ctx: BatchContext, tags: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ts": utc_ts(),
        "product_type": ctx.product_type,
        "batch_id": ctx.batch_id,
        "tags": tags,
    }

def state_payload(ctx: BatchContext, state: str, mode: str = "AUTO") -> Dict[str, Any]:
    return {
        "ts": utc_ts(),
        "product_type": ctx.product_type,
        "batch_id": ctx.batch_id,
        "state": state,
        "mode": mode,
    }

def alarm_payload(ctx: BatchContext, severity: str, code: str, message: str, **extra) -> Dict[str, Any]:
    payload = {
        "ts": utc_ts(),
        "severity": severity,
        "code": code,
        "message": message,
        "product_type": ctx.product_type,
        "batch_id": ctx.batch_id,
    }
    payload.update(extra)
    return payload

def quality_payload(ctx: BatchContext, results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ts": utc_ts(),
        "product_type": ctx.product_type,
        "batch_id": ctx.batch_id,
        "results": results,
    }

