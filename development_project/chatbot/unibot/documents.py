"""PDF generation with ReportLab.

Two kinds of document exist. Assignment *briefs* are synthetic PDFs created
once at seed time and served through a checked route. *Transcripts* are
generated on demand from whatever marks are in the database at that moment,
so a transcript is always a snapshot rather than a cached file.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .clock import to_london

INSTITUTION = "Example University (synthetic demonstration data)"


def _styles():
    return getSampleStyleSheet()


def write_assignment_brief(path: Path, assignment_id: str, module_code: str,
                           module_title: str, title: str, deadline: datetime) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=f"{module_code} {title}")
    story = [
        Paragraph(INSTITUTION, styles["Normal"]),
        Spacer(1, 6 * mm),
        Paragraph(f"{module_code}: {module_title}", styles["Title"]),
        Paragraph(f"Assignment brief: {title}", styles["Heading2"]),
        Paragraph(f"Reference: {assignment_id}", styles["Normal"]),
        Paragraph(
            f"Deadline: {to_london(deadline).strftime('%A %d %B %Y, %H:%M')} (UK time)",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            "This is a placeholder brief generated for the UniBot prototype. In a live "
            "system the module team would upload the real document and the chatbot "
            "would deliver it unchanged.",
            styles["Normal"],
        ),
    ]
    doc.build(story)


def write_transcript(path: Path, student: dict[str, Any], marks: list[dict[str, Any]]) -> None:
    """Render the student's marks to date. Pending marks stay visibly pending."""
    styles = _styles()
    doc = SimpleDocTemplate(str(path), pagesize=A4, title="Transcript of marks to date")
    cell = styles["BodyText"]
    cell.fontSize = 9
    cell.leading = 11
    # Paragraph cells wrap long module titles instead of overflowing the column.
    rows = [["Module", "Assessment", "Weight", "Mark", "Status"]]
    for mark in marks:
        rows.append([
            Paragraph(f"{mark['module_code']}<br/>{mark['title']}", cell),
            Paragraph(mark["assessment"], cell),
            f"{mark['weight']}%",
            "-" if mark["mark"] is None else str(mark["mark"]),
            mark["status"],
        ])
    table = Table(rows, colWidths=[55 * mm, 60 * mm, 20 * mm, 18 * mm, 25 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story = [
        Paragraph(INSTITUTION, styles["Normal"]),
        Spacer(1, 4 * mm),
        Paragraph("Transcript of marks to date", styles["Title"]),
        Paragraph(f"Student: {student['full_name']} ({student['student_id']})", styles["Normal"]),
        Paragraph(f"Programme: {student['programme']}", styles["Normal"]),
        Paragraph(
            "Interim document; marks marked pending have not yet been released.",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
        table,
    ]
    doc.build(story)
