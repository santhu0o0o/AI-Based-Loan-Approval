"""Every plain-English string the HTTP layer can return.

Per-field validation messages and decision reasons live in
:mod:`loanwise.domain.messages`; this module covers request-level outcomes.
Never put technical detail (exception text, stack traces) in these strings.
"""

from __future__ import annotations

from typing import Final

GENERIC_ERROR: Final = "Something went wrong on our side. Please try again in a minute."
BAD_JSON: Final = (
    "We couldn't read your answers. Please fill in the form again and press "
    "the button. If it keeps happening, refresh the page."
)
FIX_FORM: Final = "Some answers need fixing. Look for the red boxes."
NO_MODEL: Final = (
    "Our loan checker isn't ready yet. Please try again in a few minutes. "
    "(The person running this site needs to train the model first.)"
)
MODEL_INFO_UNAVAILABLE: Final = (
    "Model details aren't available yet. Please try again after the model has been trained."
)
SAMPLE_UNAVAILABLE: Final = "We couldn't load an example right now. Please fill the form yourself."
NOT_FOUND: Final = "We couldn't find that. Please check the address."
METHOD_NOT_ALLOWED: Final = "That action isn't allowed here. Please use the form on the website."
TOO_LARGE: Final = (
    "That was too much information to send at once. Please only fill in the loan form."
)

# Message for each HTTP error status on /api/*; anything else uses GENERIC_ERROR.
HTTP_ERRORS: Final[dict[int, str]] = {
    400: BAD_JSON,
    404: NOT_FOUND,
    405: METHOD_NOT_ALLOWED,
    413: TOO_LARGE,
    500: GENERIC_ERROR,
}

# Shown at / when the React app has not been built yet.
FRONTEND_MISSING_HTML: Final = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LoanWise AI</title>
<style>body{font-family:system-ui,sans-serif;max-width:560px;margin:15vh auto;padding:0 16px;
line-height:1.6;color:#1f2937;background:#f9fafb}h1{font-size:1.6rem}code{background:#e5e7eb;padding:2px 6px;border-radius:4px}</style>
</head><body><h1>LoanWise AI is almost ready</h1>
<p>The website pages haven't been built yet, but the loan checker behind them is running.</p>
<p>To build the pages, open a terminal in the <code>frontend</code> folder and run
<code>npm install</code> then <code>npm run build</code>. Then refresh this page.</p>
<p>The system check is at <a href="/api/health">/api/health</a>.</p></body></html>"""  # noqa: E501

# Shown for unexpected errors on non-API (page) requests.
PAGE_ERROR_HTML: Final = "<h1>Sorry, something went wrong.</h1><p>Please refresh the page.</p>"
