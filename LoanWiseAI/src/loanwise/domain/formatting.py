"""Display helpers shared by every user-facing message."""

from __future__ import annotations

import re

_LAKH_GROUPING = re.compile(r"(\d)(?=(\d\d)+$)")


def format_inr(amount: float) -> str:
    """Format a rupee amount with Indian digit grouping.

    Example:
        >>> format_inr(1234567)
        '₹12,34,567'
    """
    n = round(float(amount))
    sign = "-" if n < 0 else ""
    digits = str(abs(n))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        digits = _LAKH_GROUPING.sub(r"\1,", head) + "," + tail
    return f"{sign}₹{digits}"
