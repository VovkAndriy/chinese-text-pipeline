import os
import tiktoken

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4"
MAX_TOKENS = 5000


def ask_openai(system_intel: str, prompt: str, model: str = MODEL) -> str:
    result = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": prompt},
        ],
        max_tokens=MAX_TOKENS,
    )
    return result.choices[0].message.content


def count_tokens(text: str, model: str = MODEL):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
