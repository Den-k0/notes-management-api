from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY


def get_summary(content: str):
    """
    Generates a summary for the given content using the Gemini AI model.

    Args:
        content (str): The content to be summarized.

    Returns:
        str: The summary of the content.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful assistant. Your task is to provide"
                "a summary for the user's request. Return only the"
                "summary without any additional information."
                "Also, provide the summary in the same"
                "language as the input content."
            )
        ),
        contents=content
    )

    return response.text
