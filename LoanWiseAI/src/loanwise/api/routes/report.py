"""``POST /api/report/pdf`` and ``GET /api/history/<id>/pdf``: download assessment report as PDF."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, Response, jsonify, request

from loanwise.api.context import services
from loanwise.api.payload import read_payload
from loanwise.api.responses import API_PREFIX, fail
from loanwise.services.pdf_report import generate_loan_report_pdf

bp = Blueprint("report", __name__, url_prefix=API_PREFIX)


@bp.post("/report/pdf")
def download_report_pdf() -> Response | tuple[Response, int]:
    """Generate and return a PDF report from current answers and prediction result.

    Accepts JSON body:
        {
            "answers": {...},
            "result": {...},
            "id": 123 (optional)
        }
    Or:
        { "id": 123 }  (fetches from history)
    """
    payload, readable = read_payload(request)
    if not readable or not isinstance(payload, dict):
        return fail("Invalid request body. Expected JSON.", 400)

    report_id = payload.get("id")
    answers: dict[str, Any] = payload.get("answers", {})
    result: dict[str, Any] = payload.get("result", {})

    # If answers or result are missing, attempt lookup from history
    if (not answers or not result) and report_id is not None:
        try:
            item = services().history.get(int(report_id))
            if item:
                answers = answers or item.get("inputs", {})
                result = result or item.get("result", {})
                if not result:
                    result = {
                        "approved": item.get("approved"),
                        "verdict": item.get("verdict"),
                        "confidence": item.get("confidence"),
                    }
        except (ValueError, TypeError):
            pass

    if not answers and not result:
        return fail("Both answers and result are required to generate a PDF report.", 400)

    try:
        pdf_bytes = generate_loan_report_pdf(answers, result, report_id=report_id)
    except Exception as exc:
        return fail(f"Failed to generate PDF: {exc}", 500)

    filename = f"loanwise-assessment-report-{report_id or 'check'}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@bp.get("/history/<int:item_id>/pdf")
def download_history_pdf(item_id: int) -> Response | tuple[Response, int]:
    """Download PDF report for a historical check by ID."""
    item = services().history.get(item_id)
    if not item:
        return fail(f"Prediction #{item_id} not found in history.", 404)

    answers = item.get("inputs", {})
    result = item.get("result", {})
    if not result:
        result = {
            "approved": item.get("approved"),
            "verdict": item.get("verdict"),
            "confidence": item.get("confidence"),
        }

    try:
        pdf_bytes = generate_loan_report_pdf(answers, result, report_id=item_id)
    except Exception as exc:
        return fail(f"Failed to generate PDF: {exc}", 500)

    filename = f"loanwise-assessment-report-{item_id}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )
