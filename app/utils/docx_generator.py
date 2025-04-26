# from docx import Document
# from io import BytesIO

# def generate_word_doc(content: str) -> BytesIO:
#     doc = Document()  # Creates a new Word Document
#     doc.add_paragraph(content)  # Adds your generated AI content as a paragraph

#     buffer = BytesIO()  # In-memory file buffer (no need to save to disk)
#     doc.save(buffer)  # Save the doc to buffer
#     buffer.seek(0)  # Move the pointer to the start so FastAPI can read it
#     return buffer  # Return the file-like object
