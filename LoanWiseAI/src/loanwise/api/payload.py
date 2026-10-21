"""Request body decoding that never raises."""

from __future__ import annotations

import json
from typing import Any

from flask import Request

_UNREADABLE: tuple[None, bool] = (None, False)


def read_payload(request: Request) -> tuple[Any, bool]:
    """Decode the request body.

    Accepts JSON regardless of ``Content-Type`` (and the non-standard ``NaN``
    and ``Infinity`` literals, which validation then rejects per field) or a
    classic form post.

    Returns:
        ``(payload, True)`` when the body could be decoded, else ``(None, False)``.
    """
    if request.form and not request.is_json:
        return request.form.to_dict(), True
    raw = request.get_data(cache=True, as_text=False)
    if not raw or not raw.strip():
        return _UNREADABLE
    try:
        return json.loads(raw.decode("utf-8")), True
    except (UnicodeDecodeError, ValueError, RecursionError):
        return _UNREADABLE
