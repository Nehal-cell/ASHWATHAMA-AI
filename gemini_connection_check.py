import os

from dotenv import load_dotenv
from google import genai


def main():
    # Load environment variables from .env
    load_dotenv()

    # Read API key without displaying it
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print(
            "Error: GEMINI_API_KEY is missing. "
            "Please check your local .env configuration."
        )
        return

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Test the Interactions API
        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=(
                "Reply with exactly: "
                "ASHWATHAMA AI Gemini connection successful."
            ),
        )

        response_text = interaction.output_text

        if not response_text or not response_text.strip():
            print("Error: Gemini returned an empty response.")
            return

        print(response_text)

    except Exception as exc:
        # Show diagnostic details without exposing the API key
        print("Gemini connection test failed.")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error details: {exc}")


if __name__ == "__main__":
    main()