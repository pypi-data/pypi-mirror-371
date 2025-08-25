"""
z8ter.responses

Re-exports Starlette's response classes via lightweight subclasses.
Identical today, but may gain enhancements in future Z8ter releases.
"""

from __future__ import annotations

from starlette.responses import (
    Response as StarletteResponse,
    JSONResponse as StarletteJSONResponse,
    HTMLResponse as StarletteHTMLResponse,
    PlainTextResponse as StarlettePlainTextResponse,
    RedirectResponse as StarletteRedirectResponse,
    FileResponse as StarletteFileResponse,
    StreamingResponse as StarletteStreamingResponse,
)


class Response(StarletteResponse):
    """Z8ter Response (currently identical to Starlette's)."""
    pass


class JSONResponse(StarletteJSONResponse):
    """Z8ter JSONResponse (currently identical to Starlette's)."""
    pass


class HTMLResponse(StarletteHTMLResponse):
    """Z8ter HTMLResponse (currently identical to Starlette's)."""
    pass


class PlainTextResponse(StarlettePlainTextResponse):
    """Z8ter PlainTextResponse (currently identical to Starlette's)."""
    pass


class RedirectResponse(StarletteRedirectResponse):
    """Z8ter RedirectResponse (currently identical to Starlette's)."""
    pass


class FileResponse(StarletteFileResponse):
    """Z8ter FileResponse (currently identical to Starlette's)."""
    pass


class StreamingResponse(StarletteStreamingResponse):
    """Z8ter StreamingResponse (currently identical to Starlette's)."""
    pass


__all__: list[str] = [
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "RedirectResponse",
    "FileResponse",
    "StreamingResponse",
]
