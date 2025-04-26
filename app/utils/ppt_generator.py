# from pptx import Presentation
# from pptx.util import Inches, Pt
# from io import BytesIO

# def generate_ppt_doc(content: str) -> BytesIO:
#     prs = Presentation()
#     slide_layout = prs.slide_layouts[1]
#     slide = prs.slides.add_slide(slide_layout)

#     title = slide.shapes.title
#     body = slide.placeholders[1]

#     title.text = "AI Generated Content"
#     body.text = content

#     buffer = BytesIO()
#     prs.save(buffer)
#     buffer.seek(0)
#     return buffer
