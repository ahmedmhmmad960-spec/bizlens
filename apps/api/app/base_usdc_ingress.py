"""ASGI boundary for optional Base inspection requests.

This limit protects direct FastAPI callers as well as calls relayed by Next.js.
It applies only to the opt-in receipt-inspection path, not commerce CSV uploads.
"""

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

MAX_INSPECTION_BODY_BYTES = 2048
_INSPECT_PATH = "/base-usdc/inspect"
_NO_STORE = {"Cache-Control": "no-store"}


class BaseInspectionIngressLimit:
    """Reject oversized bodies as the ASGI stream arrives, before JSON parsing."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") != _INSPECT_PATH:
            await self.app(scope, receive, send)
            return

        declared = [
            value for name, value in scope.get("headers", [])
            if name.lower() == b"content-length"
        ]
        if declared:
            try:
                if len(declared) != 1 or not declared[0].isdigit():
                    raise ValueError("Malformed Content-Length.")
                body_length = int(declared[0])
            except (ValueError, OverflowError):
                response = JSONResponse(
                    status_code=400, headers=_NO_STORE,
                    content={"success": False, "error": "Invalid inspection request length."},
                )
                await response(scope, receive, send)
                return
            if body_length > MAX_INSPECTION_BODY_BYTES:
                response = JSONResponse(
                    status_code=413, headers=_NO_STORE,
                    content={"success": False, "error": "Inspection request is too large."},
                )
                await response(scope, receive, send)
                return

        received = 0

        async def bounded_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > MAX_INSPECTION_BODY_BYTES:
                    # The FastAPI body parser preserves Starlette HTTPException,
                    # and the error handler returns 413, not a parsed invoice.
                    raise HTTPException(
                        status_code=413,
                        detail="Inspection request is too large.",
                        headers=_NO_STORE,
                    )
            return message

        await self.app(scope, bounded_receive, send)
