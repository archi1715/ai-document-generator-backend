import openai
from app.config import OPENAI_API_KEY

# Set OpenAI API key from .env (already loaded in config.py)
openai.api_key = OPENAI_API_KEY

# Function to generate content using OpenAI
async def generate_content(prompt: str, language: str = "en") -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",  # You can use "gpt-3.5-turbo" if gpt-4 is not available
            messages=[
                {"role": "system", "content": "You are a helpful AI writing assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,       # Creativity level
            max_tokens=800         # Length of response
        )
        content = response.choices[0].message["content"]
        return content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, there was an error generating content."
