import os
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Set Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model  gemini-pro
model = genai.GenerativeModel("gemini-pro")  

# Generate content using Gemini
async def generate_content(prompt: str, language: str = "en") -> str:
    try:
        full_prompt = f"Language: {language}\nPrompt: {prompt}"
        response = model.generate_content(full_prompt)

        # Gemini returns response in .text
        return response.text.strip()

    except Exception as e:
        print("Gemini error:", str(e))
        traceback.print_exc()
        return "Sorry, there was an error generating content."
