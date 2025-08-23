from openai import OpenAI
from google import genai
from google.genai import types


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_response(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
            )
            return response.output_text
        except Exception as e:
            return f"OpenAI API Error: {e}"

class GoogleAIClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def get_response(self, prompt: str) -> str:
        try:
            model = "gemini-2.5-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ]
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
            result = ""
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                result += chunk.text
            return result
        except Exception as e:
            return f"Google AI API Error: {e}"

