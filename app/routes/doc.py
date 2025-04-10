from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langdetect import detect
from uuid import uuid4
from datetime import datetime
from fastapi.responses import StreamingResponse

from app.services.ai_content import generate_content
from app.db.mongo import documents_collection
from app.utils.docx_generator import generate_word_doc
from app.utils.pdf_generator import generate_pdf_doc
from app.utils.ppt_generator import generate_ppt_doc

router = APIRouter(prefix="/documents", tags=["Documents"])

class PromptRequest(BaseModel):
    prompt: str

@router.post("/")
async def create_document(request: PromptRequest):
    try:
        # 1. Generate content using AI
        content = await generate_content(request.prompt)

        # 2. Detect language
        language = detect(request.prompt)

        # 3. Create document ID
        document_id = str(uuid4())

        # 4. Prepare document
        document_data = {
            "_id": document_id,
            "prompt": request.prompt,
            "content": content,
            "language": language,
            "type": "word",  # default for now
            "created_at": datetime.utcnow()
        }

        # 5. Insert into MongoDB
        await documents_collection.insert_one(document_data)

        # 6. Return result
        return {
            "status": "success",
            "document_id": document_id,
            "content": content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 📥 Download as Word
@router.get("/download/{document_id}/word")
async def download_word(document_id: str):
    document = await documents_collection.find_one({"_id": document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    word_file = generate_word_doc(document["content"])
    return StreamingResponse(word_file, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": f"attachment; filename={document_id}.docx"
    })


# 📥 Download as PDF
@router.get("/download/{document_id}/pdf")
async def download_pdf(document_id: str):
    document = await documents_collection.find_one({"_id": document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    pdf_file = generate_pdf_doc(document["content"])
    return StreamingResponse(pdf_file, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={document_id}.pdf"
    })


# 📥 Download as PowerPoint
@router.get("/download/{document_id}/ppt")
async def download_ppt(document_id: str):
    document = await documents_collection.find_one({"_id": document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    ppt_file = generate_ppt_doc(document["content"])
    return StreamingResponse(ppt_file, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers={
        "Content-Disposition": f"attachment; filename={document_id}.pptx"
    })



