import os
from dotenv import load_dotenv
from genai_client.client import OpenAIClient
from genai_client.client import GoogleAIClient

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GEMINI_API_KEY")

openai_client = OpenAIClient(openai_api_key)
google_client = GoogleAIClient(google_api_key)

print("OpenAI Response:")
print(openai_client.get_response("hi"))

print("\nGoogle AI Response:")
print(google_client.get_response("hi"))
