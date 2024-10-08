import os
import tiktoken

from openai import AsyncClient
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncClient(api_key=OPENAI_API_KEY)

MODEL = "gpt-4"
MAX_TOKENS = 2000


async def ask_openai(system_intel: str, prompt: str, model: str = MODEL) -> str:
    """
    Function to interact with OpenAI

    :param system_intel: Information about the system or context for the conversation
    :param prompt: The input text or message for OpenAI to process.
    :param model: string of model gpt you want to use

    :return: response of OpenAI
    """
    result = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": prompt},
        ],
        max_tokens=MAX_TOKENS * 2,
    )
    return result.choices[0].message.content


def count_tokens(text: str, model: str = MODEL):
    """
    Count the number of tokens in a given text using a specified GPT model's encoding.

    :param text: The input text to be tokenized.
    :param model: The name of the GPT model to use for token encoding. Defaults to the value of `gpt-4`.

    :return: The number of tokens in the input text.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
