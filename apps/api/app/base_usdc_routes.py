"""Evidence-only Base/USDC endpoints; never changes sales or invoice balances.

The optional live endpoint is DISABLED by default. Only explicit deployment
opt-in enables a bounded read-only RPC call to the two hard-coded Base hosts.
"""
import os
from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from integrations.base_usdc.__main__ import offline_demo
from integrations.base_usdc.matcher import Invoice
from integrations.base_usdc.rpc_evidence import BasePublicRpc, inspect_invoice

router = APIRouter(prefix="/base-usdc", tags=["base-usdc-evidence"])


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


@router.post("/inspect")
def base_usdc_inspect(payload: InvoiceInspectionRequest) -> dict | JSONResponse:
    """Optional on-demand public receipt observation; never paid status."""
    if os.getenv("BIZLENS_BASE_RPC_ENABLED") != "1":
        return JSONResponse(
            status_code=503,
            headers={"Cache-Control": "no-store"},
            content={
                "success": False,
                "error": "Live RPC inspection is disabled in this demo environment.",
                "mode": "disabled",
            },
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
            content={"success": False, "error": "Invalid invoice fields; inspect the amount and addresses."},
        )

    finding = inspect_invoice(invoice, BasePublicRpc(invoice.chain_id))
    return {
        "success": True,
        "mode": "read_only_rpc",
        "network": "Base Mainnet" if invoice.chain_id == 8453 else "Base Sepolia",
        "warning": "Observed Base L2 RPC evidence is NOT proof of final settlement or paid status.",
        "result": asdict(finding),
    }
