"""PDF report generation service using ReportLab.

Produces a formal, clean, publication-grade PDF assessment report for a loan
application, detailing applicant inputs, decision verdict, confidence,
plain-English reasons, thorough financial analysis, and actionable recommendations.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from loanwise.domain.formatting import format_inr


def _clean_str(val: Any) -> str:
    """Escape text for ReportLab XML/HTML Paragraph and convert ₹ to Rs."""
    if val is None:
        return ""
    s = str(val).replace("₹", "Rs. ")
    while "Rs. Rs. " in s:
        s = s.replace("Rs. Rs. ", "Rs. ")
    while "Rs.  " in s:
        s = s.replace("Rs.  ", "Rs. ")
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _format_currency(val: Any) -> str:
    """Format rupee amount using standard 'Rs.' prefix for reliable PDF font rendering."""
    if val is None or val == "":
        return "Rs. 0"
    try:
        num = float(val)
    except (ValueError, TypeError):
        return f"Rs. {val}"
    # Use Indian grouping without the Unicode rupee symbol
    digits = format_inr(num).replace("₹", "").strip()
    return f"Rs. {digits}"


def generate_loan_report_pdf(
    answers: dict[str, Any],
    result: dict[str, Any],
    *,
    report_id: int | str | None = None,
) -> bytes:
    """Generate a high-quality PDF report as bytes.

    Args:
        answers: dictionary of applicant inputs.
        result: prediction output containing decision, verdict, reasons,
                detailed_explanation, improvement_suggestions, etc.
        report_id: optional reference identifier.

    Returns:
        bytes: Raw PDF content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1b365d")  # Deep Navy
    success_color = colors.HexColor("#166534")  # Forest Green
    danger_color = colors.HexColor("#991b1b")   # Deep Red
    text_dark = colors.HexColor("#1f2937")       # Dark Charcoal
    muted_text = colors.HexColor("#4b5563")      # Muted Gray
    border_color = colors.HexColor("#e5e7eb")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=muted_text,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
        alignment=TA_LEFT,
    )
    body_justify = ParagraphStyle(
        "BodyJustify",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=text_dark,
        alignment=TA_JUSTIFY,
    )
    bold_label = ParagraphStyle(
        "BoldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=text_dark,
    )
    reason_style = ParagraphStyle(
        "ReasonText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=muted_text,
        alignment=TA_CENTER,
    )

    story: list[Any] = []

    # 1. Header
    ref_num = f"#{report_id}" if report_id else "#" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    now_str = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")

    header_table = Table(
        [
            [
                Paragraph("<b>LoanWise AI</b>", title_style),
                Paragraph(f"<b>Assessment Reference:</b> {ref_num}<br/><b>Date:</b> {now_str}", subtitle_style),
            ],
            [
                Paragraph("AI-Driven Home Loan Underwriting Assessment &amp; Advisory Report", subtitle_style),
                "",
            ],
        ],
        colWidths=[110 * mm, 72 * mm],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("SPAN", (0, 1), (1, 1)),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8))

    # 2. Executive Verdict Card
    approved = bool(result.get("approved", False))
    verdict_text = "LIKELY APPROVED" if approved else "LIKELY REJECTED"
    badge_bg = colors.HexColor("#ecfdf5") if approved else colors.HexColor("#fef2f2")
    badge_border = success_color if approved else danger_color
    badge_text_color = success_color if approved else danger_color

    confidence = float(result.get("confidence", 0.0))
    conf_label = str(result.get("confidence_label", "Medium"))
    headline = str(result.get("headline", verdict_text))
    emi_val = result.get("emi_estimate", 0.0)
    emi_display = f"{_format_currency(emi_val)} / month" if emi_val else "N/A"

    verdict_para = Paragraph(
        f"<font size='16' color='{badge_text_color.hexval()}'><b>{verdict_text}</b></font><br/>"
        f"<font size='9' color='{text_dark.hexval()}'>{_clean_str(headline)}</font>",
        ParagraphStyle("Verdict", parent=styles["Normal"], leading=15),
    )
    metrics_para = Paragraph(
        f"<b>Confidence:</b> {confidence:.1%} ({conf_label})<br/>"
        f"<b>Estimated EMI:</b> {emi_display}<br/>"
        f"<b>Interest Rate Assumption:</b> 9.0% p.a. amortized",
        ParagraphStyle("VerdictMeta", parent=styles["Normal"], fontSize=8.5, leading=12, textColor=text_dark),
    )

    verdict_box = Table(
        [[verdict_para, metrics_para]],
        colWidths=[112 * mm, 70 * mm],
    )
    verdict_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), badge_bg),
                ("BOX", (0, 0), (-1, -1), 1.5, badge_border),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(verdict_box)
    story.append(Spacer(1, 4 * mm))

    # 3. Application Profile & Financial Metrics Table
    story.append(Paragraph("1. Application Summary &amp; Financial Assessment", section_heading))

    applicant_inc = answers.get("applicant_income", answers.get("ApplicantIncome", 0))
    coapplicant_inc = answers.get("coapplicant_income", answers.get("CoapplicantIncome", 0))
    tot_inc = float(applicant_inc or 0) + float(coapplicant_inc or 0)
    loan_amt = answers.get("loan_amount", answers.get("LoanAmount", 0))
    loan_term = answers.get("loan_term", answers.get("Loan_Amount_Term", 240))
    term_yrs = round(float(loan_term or 240) / 12.0, 1)

    cred_raw = answers.get("credit_history", answers.get("Credit_History", 1))
    cred_good = cred_raw in (1, 1.0, "1", "1.0", "yes", "good", True)
    cred_str = "Clean / Good History" if cred_good else "Adverse / Defaults Recorded"

    prop_area = str(answers.get("property_area", answers.get("Property_Area", "Semiurban"))).capitalize()
    edu = str(answers.get("education", answers.get("Education", "Graduate"))).capitalize()
    emp = "Self-Employed" if str(answers.get("self_employed", answers.get("Self_Employed", "No"))).lower() in ("yes", "1", "true") else "Salaried"
    dep = str(answers.get("dependents", answers.get("Dependents", "0")))

    fin = result.get("financial_metrics", {})
    emi_ratio_pct = fin.get("emi_to_income_pct") or (f"{(float(emi_val)/tot_inc):.1%}" if tot_inc > 0 else "N/A")
    afford_band = fin.get("affordability_band", "Manageable" if approved else "Stretched")

    profile_data = [
        [
            Paragraph("<b>Applicant Income:</b>", bold_label),
            Paragraph(f"{_format_currency(applicant_inc)} / mo", body_style),
            Paragraph("<b>Requested Loan:</b>", bold_label),
            Paragraph(f"{_format_currency(loan_amt)}", body_style),
        ],
        [
            Paragraph("<b>Co-Applicant Income:</b>", bold_label),
            Paragraph(f"{_format_currency(coapplicant_inc)} / mo", body_style),
            Paragraph("<b>Loan Tenure:</b>", bold_label),
            Paragraph(f"{term_yrs} years ({loan_term} mos)", body_style),
        ],
        [
            Paragraph("<b>Total Monthly Income:</b>", bold_label),
            Paragraph(f"{_format_currency(tot_inc)} / mo", body_style),
            Paragraph("<b>Debt-to-Income (DTI):</b>", bold_label),
            Paragraph(f"{emi_ratio_pct} ({afford_band})", body_style),
        ],
        [
            Paragraph("<b>Credit Repayment History:</b>", bold_label),
            Paragraph(cred_str, body_style),
            Paragraph("<b>Property Location:</b>", bold_label),
            Paragraph(prop_area, body_style),
        ],
        [
            Paragraph("<b>Employment &amp; Education:</b>", bold_label),
            Paragraph(f"{emp} • {edu}", body_style),
            Paragraph("<b>Dependents:</b>", bold_label),
            Paragraph(dep, body_style),
        ],
    ]

    profile_table = Table(profile_data, colWidths=[42 * mm, 50 * mm, 42 * mm, 48 * mm])
    profile_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(profile_table)
    story.append(Spacer(1, 3 * mm))

    # 4. Key Decision Reasons
    reasons = result.get("reasons", [])
    if reasons:
        story.append(Paragraph("2. Key Decision Factors", section_heading))
        reason_rows = []
        for r in reasons:
            rtype = r.get("type", "neutral")
            if rtype == "positive":
                tag = "<font color='#166534'><b>[+] HELPS CHANCES:</b></font>"
            elif rtype == "negative":
                tag = "<font color='#991b1b'><b>[-] ADVERSE FACTOR:</b></font>"
            else:
                tag = "<font color='#1f2937'><b>[i] NOTE:</b></font>"
            reason_rows.append([
                Paragraph(f"{tag} {_clean_str(r.get('text', ''))}", reason_style)
            ])
        reasons_table = Table(reason_rows, colWidths=[182 * mm])
        reasons_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f3f4f6")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(reasons_table)
        story.append(Spacer(1, 3 * mm))

    # 5. Detailed Decision Explanation
    explanation = result.get("detailed_explanation", "")
    if explanation:
        story.append(Paragraph("3. Detailed Underwriting Analysis", section_heading))
        paragraphs = [p.strip() for p in explanation.split("\n\n") if p.strip()]
        for p in paragraphs:
            story.append(Paragraph(_clean_str(p), body_justify))
            story.append(Spacer(1, 2 * mm))

    # 6. Actionable Improvement Plan / Recommendations
    suggestions = result.get("improvement_suggestions", [])
    if suggestions:
        header_title = "4. Actionable Steps to Qualify for Approval" if not approved else "4. Recommendations Prior to Loan Disbursement"
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(header_title, section_heading))

        suggestion_rows = []
        for idx, s in enumerate(suggestions, 1):
            title = _clean_str(s.get("title", ""))
            desc = _clean_str(s.get("description", ""))
            action = _clean_str(s.get("action", ""))
            cat = _clean_str(s.get("category", "Advice"))

            cell_content = (
                f"<b>{idx}. {title}</b> <font color='#4b5563'>({cat})</font><br/>"
                f"<font color='#374151'>{desc}</font><br/>"
                f"<b>Action Recommended:</b> <font color='#1b365d'>{action}</font>"
            )
            suggestion_rows.append([Paragraph(cell_content, reason_style)])

        sugg_table = Table(suggestion_rows, colWidths=[182 * mm])
        sugg_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(sugg_table)
        story.append(Spacer(1, 4 * mm))

    # 7. Disclaimer & Notice
    story.append(Spacer(1, 2 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4))
    disclaimer_text = (
        "<b>Important Notice:</b> This report is generated by LoanWise AI as an educational decision-support demonstration "
        "trained on historical mortgage datasets. It reflects machine-learning probability estimates and common-sense "
        "underwriting rules; it does not constitute a formal loan sanction, credit guarantee, or legally binding lending commitment."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return buffer.getvalue()
