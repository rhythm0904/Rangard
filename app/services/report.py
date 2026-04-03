"""
app/services/report.py
──────────────────────
Generates professional PDF scan reports using ReportLab.
"""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


DARK_BG   = colors.HexColor("#0d1117")
PURPLE    = colors.HexColor("#6e40c9")
BLUE      = colors.HexColor("#1f6feb")
TEXT      = colors.HexColor("#c9d1d9")
MUTED     = colors.HexColor("#8b949e")
DANGER    = colors.HexColor("#f85149")
WARNING   = colors.HexColor("#d29922")
SUCCESS   = colors.HexColor("#3fb950")

LEVEL_COLORS = {
    "critical": colors.HexColor("#7d1a1a"),
    "high":     colors.HexColor("#7c2d12"),
    "medium":   colors.HexColor("#713f12"),
    "low":      colors.HexColor("#14532d"),
    "clean":    colors.HexColor("#166534"),
}


def generate_pdf_report(scan, user) -> bytes:
    """
    Generate a PDF report for a completed scan.

    Args:
        scan: FileScan ORM object
        user: User ORM object

    Returns:
        PDF as bytes (ready to stream to the browser)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Title ────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=22,
        textColor=PURPLE,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MUTED,
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=PURPLE,
        spaceBefore=12,
        spaceAfter=6,
    )

    story.append(Paragraph("🛡️ RANGARD", title_style))
    story.append(Paragraph("Security Scan Report", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=12))

    # ── Metadata table ────────────────────────────────────────────────────
    threat_level = (scan.threat_level.value if scan.threat_level else "unknown")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    meta_data = [
        ["Report generated", generated_at],
        ["User", user.email],
        ["Scan ID", scan.id],
        ["File name", scan.original_filename],
        ["File size", f"{scan.file_size_bytes:,} bytes"],
        ["MIME type", scan.mime_type or "Unknown"],
        ["SHA-256", scan.sha256_hash],
        ["Scan duration", f"{scan.scan_duration_ms or 0} ms"],
        ["Scan status", scan.status.value.title()],
    ]
    meta_table = Table(meta_data, colWidths=[45 * mm, 130 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR",   (1, 0), (1, -1), colors.black),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
        ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ── Threat assessment ─────────────────────────────────────────────────
    story.append(Paragraph("Threat Assessment", heading_style))

    level_color = LEVEL_COLORS.get(threat_level, colors.grey)
    confidence_pct = round((scan.confidence_score or 0) * 100, 1)

    threat_data = [
        ["Threat level", threat_level.upper()],
        ["Confidence score", f"{confidence_pct}%"],
        ["Quarantined", "Yes" if scan.quarantine else "No"],
        ["Blockchain anchored", "Yes" if scan.blockchain else "No"],
    ]
    if scan.blockchain:
        threat_data.append(["Transaction hash", scan.blockchain.tx_hash])
        threat_data.append(["Network", scan.blockchain.network])

    threat_table = Table(threat_data, colWidths=[45 * mm, 130 * mm])
    threat_table.setStyle(TableStyle([
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR",   (1, 0), (1, -1), colors.black),
        ("BACKGROUND",  (1, 0), (1, 0), level_color),
        ("TEXTCOLOR",   (1, 0), (1, 0), colors.white),
        ("FONTNAME",    (1, 0), (1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
        ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(threat_table)
    story.append(Spacer(1, 12))

    # ── Detected patterns ─────────────────────────────────────────────────
    if scan.detected_patterns:
        story.append(Paragraph("Detected Patterns", heading_style))
        for pattern in scan.detected_patterns:
            story.append(Paragraph(f"• {pattern}", body_style))
        story.append(Spacer(1, 8))

    # ── Technical features ────────────────────────────────────────────────
    if scan.ml_features:
        story.append(Paragraph("Technical Analysis", heading_style))
        feats = scan.ml_features
        tech_data = [["Feature", "Value"]]
        display_features = [
            ("File entropy", f"{feats.get('entropy_full', 0):.3f} / 8.0"),
            ("Header entropy", f"{feats.get('entropy_header', 0):.3f} / 8.0"),
            ("PE executable", "Yes" if feats.get("is_pe") else "No"),
            ("PE section count", str(feats.get("pe_section_count", "N/A"))),
            ("Ransomware string hits", str(feats.get("ransom_string_hits", 0))),
            ("Printable byte ratio", f"{feats.get('printable_ratio', 0):.1%}"),
            ("Null byte ratio", f"{feats.get('null_byte_ratio', 0):.1%}"),
        ]
        tech_data.extend(display_features)
        tech_table = Table(tech_data, colWidths=[70 * mm, 105 * mm])
        tech_table.setStyle(TableStyle([
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("BACKGROUND",  (0, 0), (-1, 0), PURPLE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR",   (0, 1), (0, -1), MUTED),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
            ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
            ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(tech_table)

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Spacer(1, 6))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8, textColor=MUTED
    )
    story.append(Paragraph(
        f"Generated by RANGARD AI Security Platform · {generated_at} · "
        f"This report is confidential and intended solely for {user.email}",
        footer_style,
    ))

    doc.build(story)
    return buffer.getvalue()
