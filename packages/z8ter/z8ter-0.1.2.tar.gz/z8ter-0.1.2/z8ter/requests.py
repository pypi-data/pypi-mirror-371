"""
z8ter.requests
Re-exports Starlette's Request class. Identical today, but may
gain enhancements in future Z8ter releases.
"""
from __future__ import annotations
from starlette.requests import Request as StarletteRequest


class Request(StarletteRequest):
    """Z8ter's Request (currently identical to Starlette's)."""
    pass


__all__: list[str] = ["Request"]
