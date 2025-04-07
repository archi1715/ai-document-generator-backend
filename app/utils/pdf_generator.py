from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf_doc(content: str) -> BytesIO:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Simple wrap for long text
    lines = content.split("\n")
    y = height - 40
    for line in lines:
        if y < 40:
            pdf.showPage()
            y = height - 40
        pdf.drawString(40, y, line)
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer
