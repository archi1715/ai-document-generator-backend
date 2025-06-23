from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from langdetect import detect
from uuid import uuid4
from datetime import datetime
from fastapi.responses import StreamingResponse
from fastapi import Path, Query
from typing import List
from bson import ObjectId

from app.db.mongo import get_documents_collection, get_document_history_collection, get_presentation_collection
from app.services.ai_content import generate_content
from app.utils.docx_generator import generate_word_doc
from app.utils.pdf_generator import generate_pdf_doc
from app.utils.ppt_generator import generate_ppt_doc
from app.auth.dependencies import get_current_user
from app.models.document import DocumentHistory

router = APIRouter(prefix="/documents", tags=["Documents"])

class PromptRequest(BaseModel):
    prompt: str

class UpdateDocument(BaseModel):
    content: str

@router.post("/")
async def create_document(request: PromptRequest, user=Depends(get_current_user)):
    try:
        content = await generate_content(request.prompt)
        language = detect(request.prompt)
        document_id = str(ObjectId())

        document_data = {
            "_id": ObjectId(document_id),
            "user_email": user["email"],
            "prompt": request.prompt,
            "content": content,
            "language": language,
            "type": "word",
            "created_at": datetime.utcnow()
        }

        await get_documents_collection().insert_one(document_data)

        return {
            "status": "success",
            "document_id": document_id,
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert-presentation-to-document/{presentation_id}")
async def convert_presentation_to_document(presentation_id: str, user=Depends(get_current_user)):
    try:
        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found.")

        content = ""
        for slide in presentation["slides"]:
            content += f"Slide {slide['slide_number']} - {slide['title']}\n"
            content += f"{slide['description']}\n\n"

        document_id = str(ObjectId())
        document_data = {
            "_id": ObjectId(document_id),
            "user_email": user["email"],
            "prompt": presentation["prompt"],
            "content": content,
            "language": detect(presentation["prompt"]),
            "type": "ppt",
            "created_at": datetime.utcnow()
        }

        await get_documents_collection().insert_one(document_data)

        return {"status": "success", "document_id": document_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{document_id}/word")
async def download_word(document_id: str):
    document = await get_documents_collection().find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    word_file = generate_word_doc(document["content"])
    return StreamingResponse(word_file, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": f"attachment; filename={document_id}.docx"
    })

@router.get("/download/{document_id}/pdf")
async def download_pdf(document_id: str):
    document = await get_documents_collection().find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_file = generate_pdf_doc(document["content"])
    return StreamingResponse(pdf_file, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={document_id}.pdf"
    })

@router.get("/download/{document_id}/ppt")
async def download_ppt(document_id: str):
    document = await get_documents_collection().find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    ppt_file = generate_ppt_doc(document["content"])
    return StreamingResponse(ppt_file, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers={
        "Content-Disposition": f"attachment; filename={document_id}.pptx"
    })

@router.get("/user-documents")
async def get_user_documents(user=Depends(get_current_user)):
    documents = await get_documents_collection().find({"user_email": user["email"]}).to_list(length=100)
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return {"documents": documents}

@router.delete("/{document_id}")
async def delete_document(document_id: str = Path(..., description="Document ID to delete"), user=Depends(get_current_user)):
    result = await get_documents_collection().delete_one({
        "_id": ObjectId(document_id),
        "user_email": user["email"]
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")

    return {"status": "success", "message": "Document deleted"}

@router.put("/{document_id}")
async def update_document(document_id: str, update: UpdateDocument, user=Depends(get_current_user)):
    result = await get_documents_collection().update_one(
        {"_id": ObjectId(document_id), "user_email": user["email"]},
        {"$set": {"content": update.content}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")

    return {"status": "success", "message": "Document updated"}

@router.get("/history", response_model=List[DocumentHistory])
async def get_user_history(user=Depends(get_current_user)):
    collection = get_document_history_collection()
    history = await collection.find({"user_email": user["email"]}).to_list(length=100)
    return history

@router.get("/search", response_model=List[DocumentHistory])
async def search_documents_by_title(query: str = Query(...), user=Depends(get_current_user)):
    collection = get_document_history_collection()
    results = await collection.find({
        "user_email": user["email"],
        "title": {"$regex": query, "$options": "i"}
    }).to_list(length=100)
    return results
