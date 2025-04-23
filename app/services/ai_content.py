import openai
import traceback
from app.config import OPENAI_API_KEY

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# Function to generate content using OpenAI
async def generate_content(prompt: str, language: str = "en") -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if needed and allowed
            messages=[
                {"role": "system", "content": "You are a helpful AI writing assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        return content

    except Exception as e:
        print("OpenAI error:", str(e))
        traceback.print_exc()
        return "Sorry, there was an error generating content."

# Uncomment this if you want to temporarily switch to mock response
"""
async def generate_content(prompt: str, language: str = "en") -> str:
    try:
        fake_response = f"This is a mock response for the prompt: '{prompt}'"
        return fake_response
    except Exception as e:
        print("Mocked generation error:", str(e))
        traceback.print_exc()
        return "Sorry, mock generation failed."
"""
