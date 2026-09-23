"""Render the lesson and the rejection log as PDF files (reportlab)."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from models.models import EvaluationState, Lesson, RejectionRecord

_MARGIN = 2.2 * cm
_NAVY = colors.HexColor("#1F3A5F")
_RED = colors.HexColor("#8A1C1C")

# Punctuation the built-in PDF fonts lack (they would print as black boxes).
_ASCII_FALLBACKS = {"\u2192": "->", "\u2190": "<-", "\u2011": "-", "\u2212": "-", "\u00a0": " "}


def _make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=base["Normal"], fontSize=11.5, leading=17, spaceAfter=6)
    return {
        "title": ParagraphStyle(
            "LessonTitle", parent=base["Title"], fontSize=22, leading=27, alignment=0, spaceAfter=10
        ),
        "heading": ParagraphStyle(
            "LessonHeading", parent=base["Heading2"], fontSize=14, spaceBefore=14, spaceAfter=4, textColor=_NAVY
        ),
        "body": body,
        "banner": ParagraphStyle(
            "Banner",
            parent=body,
            fontName="Helvetica-Bold",
            textColor=_RED,
            backColor=colors.HexColor("#FBE9E9"),
            borderColor=_RED,
            borderWidth=1,
            borderPadding=8,
        ),
    }


STYLES = _make_styles()


# --- public API ------------------------------------------------------------


def write_lesson_pdf(lesson: Lesson, path: Path, banner: str | None = None) -> Path:
    """Write the lesson to `path`. A `banner` is printed in red above the title."""

    story: list[Flowable] = []
    if banner:
        story += [Paragraph(_markup(banner), STYLES["banner"]), Spacer(1, 14)]

    story += [
        Paragraph(_markup(lesson.title), STYLES["title"]),
        Paragraph(_markup(lesson.introduction), STYLES["body"]),
        *_section("What is it?", [lesson.definition]),
        *_section("Why does it matter?", [lesson.why]),
        *_heading_and_list("How does it work?", [_markup(s) for s in lesson.workflow], numbered=True),
        *_heading_and_list("Example", [_markup(s) for s in lesson.example], numbered=False),
        *_heading_and_list("Key terms", _key_term_markups(lesson), numbered=False),
        *_section("Summary", [lesson.summary]),
    ]
    return _build(path, story, title=lesson.title)


def write_rejection_log_pdf(state: EvaluationState, path: Path) -> Path:
    """Write every rejection of the run: what failed, why, and what was asked to change."""

    passed = state.final_status == "PASS"
    result = (
        f"Passed on attempt {state.attempt}."
        if passed
        else f"Failed after {state.attempt} attempts (not shipped)."
    )
    story: list[Flowable] = [
        Paragraph("Rejection log", STYLES["title"]),
        Paragraph(f"<b>Topic:</b> {_markup(state.topic)}", STYLES["body"]),
        Paragraph(f"<b>Final result:</b> {_markup(result)}", STYLES["body"]),
    ]

    if not state.rejection_log:
        story.append(Paragraph("No rejections: the first attempt passed every check.", STYLES["body"]))
    last_index = len(state.rejection_log) - 1
    for index, record in enumerate(state.rejection_log):
        story += _rejection_section(record, retry_followed=passed or index < last_index)
    return _build(path, story, title=f"Rejection log - {state.topic}")


# --- building blocks -------------------------------------------------------


def _rejection_section(record: RejectionRecord, retry_followed: bool) -> list[Flowable]:
    failures = [
        f"<b>{_markup(criterion)}</b>: {_markup(reason)}"
        for criterion, reason in zip(record.failed_criteria, record.reasons)
    ]
    instructions = [_markup(text) for text in record.regeneration_instructions] or [
        "No instructions were recorded."
    ]
    followup = (
        "These instructions were applied in the next attempt."
        if retry_followed
        else "No further attempt was made: the retry limit was reached."
    )
    return [
        Paragraph(f"Attempt {record.attempt}: rejected", STYLES["heading"]),
        Paragraph("<b>What failed and why</b>", STYLES["body"]),
        _list(failures, numbered=False),
        Paragraph("<b>What the evaluator asked to change</b>", STYLES["body"]),
        _list(instructions, numbered=False),
        Paragraph(f"<i>{_markup(followup)}</i>", STYLES["body"]),
    ]


def _section(heading: str, paragraphs: list[str]) -> list[Flowable]:
    return [
        Paragraph(_markup(heading), STYLES["heading"]),
        *(Paragraph(_markup(text), STYLES["body"]) for text in paragraphs),
    ]


def _heading_and_list(heading: str, markups: list[str], numbered: bool) -> list[Flowable]:
    return [Paragraph(_markup(heading), STYLES["heading"]), _list(markups, numbered)]


def _list(markups: list[str], numbered: bool) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(markup, STYLES["body"]), leftIndent=18) for markup in markups],
        bulletType="1" if numbered else "bullet",
        bulletFormat="%s." if numbered else None,
        leftIndent=18,
    )


def _key_term_markups(lesson: Lesson) -> list[str]:
    return [
        f"<b>{_markup(term)}</b>: {_markup(meaning)}" if meaning else f"<b>{_markup(term)}</b>"
        for term, meaning in (_term_pair(item) for item in lesson.key_terms)
    ]


def _term_pair(item: dict[str, str]) -> tuple[str, str]:
    """key_terms are loosely typed dicts: accept {"term", "meaning"} or {term: meaning}."""
    if "term" in item:
        return item["term"], " ".join(v for k, v in item.items() if k != "term")
    if len(item) == 1:
        ((term, meaning),) = item.items()
        return term, meaning
    values = list(item.values())
    return (values[0], " ".join(values[1:])) if values else ("", "")


def _plain(text: str) -> str:
    """Text the built-in fonts can draw: fancy arrows become ASCII, unknown characters become '?'."""
    for char, replacement in _ASCII_FALLBACKS.items():
        text = text.replace(char, replacement)
    return text.encode("cp1252", errors="replace").decode("cp1252")


def _markup(text: str) -> str:
    """Escape for reportlab's mini-HTML so model output can never break the layout."""
    return escape(_plain(text)).replace("\n", "<br/>")


def _footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - _MARGIN, 1.2 * cm, f"Page {document.page}")
    canvas.restoreState()


def _build(path: Path, story: list[Flowable], title: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        title=_plain(title),
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
    )
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return path