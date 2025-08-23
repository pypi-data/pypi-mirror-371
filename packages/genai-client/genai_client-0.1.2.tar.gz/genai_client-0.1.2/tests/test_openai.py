from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="o4-mini",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)