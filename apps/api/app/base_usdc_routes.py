"""Evidence-only Base/USDC endpoints; never changes sales or invoice balances.

The optional live endpoint is DISABLED by default. Only explicit deployment
opt-in enables a bounded read-only RPC call to the two hard-coded Base hosts.
"""
import hmac
import os
import re
import threading
import time
from collections import deque
from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from integrations.base_usdc.__main__ import offline_demo
from integrations.base_usdc.matcher import Invoice
from integrations.base_usdc.rpc_evidence import BasePublicRpc, inspect_invoice

router = APIRouter(prefix="/base-usdc", tags=["base-usdc-evidence"])

# Single-process demo guard. Public deployments need shared rate limits at a gateway.
_MAX_RPC_PER_MINUTE = 10
_RPC_WINDOW_SECONDS = 60
_rpc_lock = threading.Lock()
_rpc_slots = threading.BoundedSemaphore(2)
_recent_rpc_calls: deque[float] = deque()


def _admit_rpc() -> bool:
    with _rpc_lock:
        now = time.monotonic()
        while _recent_rpc_calls and now - _recent_rpc_calls[0] >= _RPC_WINDOW_SECONDS:
            _recent_rpc_calls.popleft()
        if len(_recent_rpc_calls) >= _MAX_RPC_PER_MINUTE:
            return False
        _recent_rpc_calls.append(now)
        return True



class InvoiceInspectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    invoice_id: str = Field(min_length=1, max_length=80)
    chain_id: Literal[8453, 84532]
    recipient: str = Field(min_length=42, max_length=42)
    amount_usdc: str = Field(min_length=1, max_length=64)
    tx_hash: str = Field(min_length=66, max_length=66)
    log_index: Annotated[int, Field(strict=True, ge=0, le=100_000_000)] | None = None


@router.get("/demo")
def base_usdc_demo() -> dict:
    """Synthetic fixtures, no networking or blockchain claims."""
    return {"success": True, **offline_demo()}


@router.post("/inspect", response_model=None)
def base_usdc_inspect(
    payload: InvoiceInspectionRequest,
    inspection_key: Annotated[str | None, Header(alias="X-BizLens-Rpc-Key")] = None,
) -> JSONResponse:
    """Optional on-demand public receipt observation; never paid status."""
    configured = os.getenv("BIZLENS_BASE_RPC_TOKEN", "")
    if os.getenv("BIZLENS_BASE_RPC_ENABLED") != "1" or not re.fullmatch(
        r"[0-9a-f]{64}", configured
    ):
        return JSONResponse(
            status_code=503,
            headers={"Cache-Control": "no-store"},
            content={
                "success": False,
                "error": "Live RPC inspection is disabled in this demo environment.",
                "mode": "disabled",
            },
        )
    if not hmac.compare_digest(inspection_key or "", configured):
        return JSONResponse(
            status_code=403,
            headers={"Cache-Control": "no-store"},
            content={"success": False, "error": "Authorized inspector access required."},
        )
    try:
        invoice = Invoice(
            invoice_id=payload.invoice_id,
            chain_id=payload.chain_id,
            recipient=payload.recipient,
            amount_usdc=payload.amount_usdc,
            tx_hash=payload.tx_hash,
            log_index=payload.log_index,
        )
    except ValueError:
        return JSONResponse(
            status_code=422,
            headers={"Cache-Control": "no-store"},
            content={
                "success": False,
                "error": "Invalid invoice fields; inspect the amount and addresses.",
            },
        )

    if not _rpc_slots.acquire(blocking=False):
        return JSONResponse(
            status_code=429,
            headers={"Cache-Control": "no-store", "Retry-After": "10"},
            content={"success": False, "error": "RPC inspection is busy. Try later."},
        )
    try:
        if not _admit_rpc():
            return JSONResponse(
                status_code=429,
                headers={"Cache-Control": "no-store", "Retry-After": "60"},
                content={"success": False, "error": "RPC demo rate limit reached. Try later."},
            )
        finding = inspect_invoice(invoice, BasePublicRpc(invoice.chain_id))
        return JSONResponse(
            headers={"Cache-Control": "no-store"},
            content={
                "success": True,
                "mode": "read_only_rpc",
                "network": "Base Mainnet" if invoice.chain_id == 8453 else "Base Sepolia",
                "warning": (
                    "Observed Base L2 RPC evidence is NOT proof of "
                    "final settlement or paid status."
                ),
                "result": asdict(finding),
            },
        )
    finally:
        _rpc_slots.release()
