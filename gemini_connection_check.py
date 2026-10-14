
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY .env file mein nahi mili."
    )

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=(
            "Reply with exactly: "
            "ASHWATHAMA AI Gemini connection successful."
        ),
    )
    print(response.text)

except errors.APIError as exc:
    print(f"Gemini API error: {exc.code}")
    print(exc.message)
