import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from app.models.ppt import SlideContent

load_dotenv()
logger = logging.getLogger(__name__)

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ List of fallback models
MODEL_FALLBACKS = [
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash",
    "models/gemini-1.0-pro-vision-latest",
]


async def generate_slide_outline(prompt: str, num_slides: int = 10):
    result = []

    for i in range(num_slides):
        slide_generated = False
        for model_name in MODEL_FALLBACKS:
            try:
                model = genai.GenerativeModel(model_name)
                chat = model.start_chat()
                message = (
                    f"Generate slide {i+1} for a presentation on '{prompt}'.\n"
                    "Return a slide title and a short 1–2 sentence description (NO bullet points).\n"
                    "Format response as:\nTitle: <Slide Title>\nDescription: <Description>"
                )

                response = chat.send_message(message)
                text = response.text.strip()
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                title = ""
                description = ""

                for line in lines:
                    if not title and "title" in line.lower():
                        title = line.split(":", 1)[-1].strip()
                    elif not description and "description" in line.lower():
                        description = line.split(":", 1)[-1].strip()
                    elif not description:
                        description = line.strip()

                result.append({
                    "slide_number": i + 1,
                    "title": title if title else f"Slide {i+1}",
                    "description": description if description else "No description provided."
                })

                slide_generated = True
                break

            except Exception as e:
                logger.warning(f"❌ Model {model_name} failed on slide {i+1}: {str(e)}")

        if not slide_generated:
            result.append({
                "slide_number": i + 1,
                "title": f"Slide {i+1} (Error)",
                "description": "Could not generate content."
            })

    return result


async def generate_slide_content_with_image(outline):
    for model_name in MODEL_FALLBACKS:
        try:
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat()
            message = (
                f"You are generating slide content.\n"
                f"Title: {outline.title}\n"
                f"Description: {outline.description}\n"
                "Return:\n"
                "- 3 to 5 concise bullet points.\n"
                "- A single sentence image suggestion at the end (starting with 'Image:' or 'Suggested image:')."
            )

            response = chat.send_message(message)
            text = response.text.strip()
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            bullet_points = []
            image_prompt = "No image suggestion found."

            for line in lines:
                if line.startswith(("-", "*", "•")):
                    bullet_points.append(line.lstrip("-*• ").strip())
                elif line.lower().startswith("image:") or "image" in line.lower():
                    image_prompt = line.split(":", 1)[-1].strip()

            return SlideContent(
                slide_number=outline.slide_number,
                title=outline.title,
                bullet_points=bullet_points or ["No bullet points generated."],
                image_prompt=image_prompt
            )

        except Exception as e:
            logger.warning(f"❌ Model {model_name} failed on slide {outline.slide_number}: {str(e)}")

    return SlideContent(
        slide_number=outline.slide_number,
        title=f"{outline.title} (Error)",
        bullet_points=["Could not generate bullet points."],
        image_prompt="Could not generate image prompt."
    )
