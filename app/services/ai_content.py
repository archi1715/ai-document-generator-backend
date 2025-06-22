from openai import OpenAI
from app.config import OPENAI_API_KEY
import traceback

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)

# # Function to generate content using OpenAI
# async def generate_content(prompt: str, language: str = "en") -> str:
#     try:
#         response = await client.chat.completions.create(
#             model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access
#             messages=[
#                 {"role": "system", "content": "You are a helpful AI writing assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=300
#         )
#         content = response.choices[0].message.content
#         return content

#     except Exception as e:
#         print("OpenAI error:", str(e))
#         traceback.print_exc()  # Good for debugging during dev
#         raise e  # Let FastAPI handle the HTTP error response
#                        or
# return "Sorry, there was an error generating content."

# Simulate OpenAI content generation (for free dev testing)
async def generate_content(prompt: str, language: str = "en") -> str:
    try:
        # You can change this static response to anything you want
        fake_response = f"This is a mock response for the prompt: '{prompt}'"
        return fake_response
    except Exception as e:
        print("Gemini error:", str(e))
        traceback.print_exc()
        return "Sorry, mock generation failed."
