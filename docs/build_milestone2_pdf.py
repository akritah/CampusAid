"""Build the compact Milestone 2 BMC and technical summary PDF."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


OUT = Path(__file__).with_name("CampusAid_Milestone2.pdf")
PAGE = landscape(letter)
NAVY = colors.HexColor("#14233B")
GOLD = colors.HexColor("#D9A441")
INK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#5B6574")
PALE = colors.HexColor("#F4F6F9")
WHITE = colors.white

blocks = [
    ("Key Partners", "Universities and student-affairs offices; cloud hosting and database providers; Gemini API provider; campus IT and policy owners."),
    ("Key Activities", "Maintain complaint intake and tracking; curate current policy files; evaluate classification and answer grounding; operate security, storage, backups, and support."),
    ("Value Propositions", "One portal for submitting and tracking grievances; multilingual voice intake; automatic complaint classification; policy answers grounded in university documents with citations."),
    ("Customer Relationships", "Student self-service and case tracking; clear status updates; escalation to responsible university offices; onboarding and support for administrators."),
    ("Customer Segments", "Universities and colleges; students submitting concerns; faculty, wardens, and student-affairs staff handling cases."),
    ("Key Resources", "Next.js and FastAPI application; multilingual classifier; policy corpus and RAG pipeline; secure database and persistent storage; institutional policy expertise."),
    ("Channels", "University-branded web portal; links from ERP/LMS; orientation materials; QR codes and student-affairs communications."),
    ("Cost Structure", "Hosting and persistent storage; database and backups; Gemini API usage; voice-transcription compute; implementation, support, security, and policy review."),
    ("Revenue Streams", "Proposed campus subscription or institutional license, plus setup and support. This is a business hypothesis; the prototype has no current revenue."),
]


def draw_paragraph(c, text, x, y_top, width, style):
    p = Paragraph(escape(text), style)
    _, height = p.wrap(width, 1000)
    p.drawOn(c, x, y_top - height)
    return height


def header(c, title, subtitle, page_no):
    c.setFillColor(NAVY)
    c.rect(0, PAGE[1] - 78, PAGE[0], 78, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, PAGE[1] - 82, PAGE[0], 4, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(28, PAGE[1] - 39, title)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#D7DFEB"))
    c.drawString(29, PAGE[1] - 58, subtitle)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE[0] - 28, 18, f"CampusAid | Milestone 2 | {page_no}")


def build():
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    c.setTitle("CampusAid - Milestone 2")
    c.setAuthor("CampusAid project team")

    header(c, "CampusAid | Business Model Canvas", "Student grievance support and policy Q&A | Proposed institutional product model", 1)
    margin, gap = 28, 10
    top = PAGE[1] - 98
    bottom = 31
    card_w = (PAGE[0] - 2 * margin - 2 * gap) / 3
    card_h = (top - bottom - 2 * gap) / 3
    title_style = ParagraphStyle("card-title", fontName="Helvetica-Bold", fontSize=9.2, leading=11, textColor=WHITE, alignment=TA_LEFT)
    body_style = ParagraphStyle("card-body", fontName="Helvetica", fontSize=8.1, leading=10.2, textColor=INK)

    for index, (title, body) in enumerate(blocks):
        row, col = divmod(index, 3)
        x = margin + col * (card_w + gap)
        y = top - (row + 1) * card_h - row * gap
        c.setFillColor(PALE)
        c.roundRect(x, y, card_w, card_h, 7, stroke=0, fill=1)
        c.setFillColor(NAVY if index not in {2, 4} else colors.HexColor("#243C60"))
        c.roundRect(x, y + card_h - 29, card_w, 29, 7, stroke=0, fill=1)
        c.rect(x, y + card_h - 29, card_w, 7, stroke=0, fill=1)
        draw_paragraph(c, title, x + 10, y + card_h - 8, card_w - 20, title_style)
        draw_paragraph(c, body, x + 10, y + card_h - 39, card_w - 20, body_style)
    c.showPage()

    header(c, "Technical Summary and Evaluation", "Prototype architecture, answer grounding, observed checks, and known limits", 2)
    x, width = 34, PAGE[0] - 68
    y = PAGE[1] - 105
    sections = [
        ("Objective", "CampusAid combines authenticated student grievance submission and tracking with voice complaint intake and document-grounded policy questions."),
        ("Architecture", "Next.js 15 frontend; FastAPI backend; SQLAlchemy with SQLite locally and PostgreSQL for hosting; multilingual sentence-transformer embeddings plus a scikit-learn complaint classifier; Faster-Whisper on CPU for voice; Gemini Interactions API for policy answer generation."),
        ("Policy Q&A", "PDF, DOCX, Markdown, and text files are extracted and chunked. Normalized lexical overlap retrieves passages; Gemini answers using those passages and cites filenames. Without a relevant passage, it provides general guidance without stating that it is Bennett policy. The attendance answer is grounded in Section 10 of the 2024-25 Examination Manual."),
        ("Prompt and Test Design", "Prompt snapshots v1-v3 and the final prompt are in the repository. The fixed cases cover 75% attendance, grievance filing, and an unsupported student-ID question. On 2026-11-21, manual checks verified two cited policy answers and one general answer with no policy citation; a direct Gemini request also succeeded."),
        ("Limitations", "The retrieval method is lexical, not vector search. Several official PDFs are scans and require OCR. The attendance manual is AY2024-25, so current-year rules should be confirmed. The prototype has not completed independent production or load testing."),
        ("Submission details", "Team members: add the names and student IDs from the project team before submission. The public source repository is https://github.com/akritah/CampusAid. A public app URL and dedicated evaluator login are pending deployment and must be filled in Q23."),
    ]
    heading_style = ParagraphStyle("section-heading", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY)
    text_style = ParagraphStyle("section-text", fontName="Helvetica", fontSize=9.2, leading=13, textColor=INK)
    for title, body in sections:
        c.setFillColor(GOLD)
        c.roundRect(x, y - 2, 5, 18, 2, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 14, y + 1, title)
        y -= 21
        h = draw_paragraph(c, body, x + 14, y, width - 14, text_style)
        y -= h + 13
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
