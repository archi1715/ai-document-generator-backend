from fastapi import APIRouter, HTTPException
from typing import List
from app.utils.gemini_ai import generate_slide_outline, generate_slide_content_with_image
from app.models.ppt import PromptRequest, SlideOutline, SlideContent, UpdateSlidePromptRequest
from bson import ObjectId
from app.db.mongo import get_presentation_collection

router = APIRouter(prefix="/api/ppt", tags=["Presentation"])

# Generate slide outline and save with unique presentation_id
@router.post("/generate-outline")
async def generate_presentation_outline(prompt_data: PromptRequest):
    try:
        presentation_id = str(ObjectId())
        slides = await generate_slide_outline(prompt_data.prompt, prompt_data.num_slides or 10)

        for i, slide in enumerate(slides):
            slide["slide_number"] = i + 1

        collection = get_presentation_collection()
        await collection.insert_one({
            "_id": ObjectId(presentation_id),
            "presentation_id": presentation_id,
            "prompt": prompt_data.prompt,
            "slides": slides
        })

        return {
            "presentation_id": presentation_id,
            "slides": slides
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get outline by presentation_id
@router.get("/outline/{presentation_id}", response_model=List[SlideOutline])
async def get_outline_by_id(presentation_id: str):
    try:
        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        return presentation["slides"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update one slide and return full updated slides
@router.put("/update-slide-prompt/{presentation_id}/{slide_number}", response_model=List[SlideOutline])
async def update_slide_prompt(presentation_id: str, slide_number: int, data: UpdateSlidePromptRequest):
    try:
        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")

        updated_slide = await generate_slide_outline(data.new_prompt, 1)
        updated_slide[0]["slide_number"] = slide_number

        for idx, slide in enumerate(presentation["slides"]):
            if slide["slide_number"] == slide_number:
                presentation["slides"][idx] = updated_slide[0]
                break

        await collection.update_one(
            {"presentation_id": presentation_id},
            {"$set": {"slides": presentation["slides"]}}
        )

        return presentation["slides"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate full slide content for export
@router.post("/generate-slides/{presentation_id}", response_model=List[SlideContent])
async def generate_slide_content(presentation_id: str):
    try:
        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})

        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")

        results = []
        for slide_dict in presentation["slides"]:
            outline = SlideOutline(**slide_dict)
            content = await generate_slide_content_with_image(outline)
            results.append(content)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/slide/{presentation_id}/{slide_number}")
async def delete_slide(presentation_id: str, slide_number: int):
    try:
        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")

        slides = [s for s in presentation["slides"] if s["slide_number"] != slide_number]
        for i, s in enumerate(slides):
            s["slide_number"] = i + 1

        await collection.update_one(
            {"presentation_id": presentation_id},
            {"$set": {"slides": slides}}
        )

        return {"status": "deleted", "slide_number": slide_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slide/add", response_model=SlideOutline)
async def add_slide(prompt: str, presentation_id: str, slide_number: int):
    try:
        new_slide = await generate_slide_outline(prompt, 1)
        new_slide[0]["slide_number"] = slide_number

        collection = get_presentation_collection()
        presentation = await collection.find_one({"presentation_id": presentation_id})
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")

        slides = presentation["slides"]
        slides.insert(slide_number - 1, new_slide[0])
        for i, s in enumerate(slides):
            s["slide_number"] = i + 1

        await collection.update_one(
            {"presentation_id": presentation_id},
            {"$set": {"slides": slides}}
        )

        return new_slide[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


