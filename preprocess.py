import asyncio
import re
import json

from config import system_to_retrieve_words
from openai_request import (
    ask_openai,
    count_tokens,
    MAX_TOKENS
)
from math import ceil


def divide_into_paragraphs(text: str) -> list:
    """Splits the input text into paragraphs"""
    return [
        paragraph
        for paragraph in text.split('\n')
        if paragraph
    ]


def divide_into_sentences(paragraph: str) -> list:
    """
    Divides paragraph into individual sentences.
    It uses split function by chinese punctuation (。！？)
    It counts quotes before punctuation that was found
    and if that count is even -> return sentence
        if not -> continue, because we want full sentence, not a part of it
    """
    ending_pattern = re.compile(r'([。！？])')
    quote_pattern = re.compile(r'["“”]')

    combine_sentence_with_ending = []
    last_end = 0

    for match in ending_pattern.finditer(paragraph):
        end_pos = match.start() + 1

        quotes_before = quote_pattern.findall(paragraph[last_end:end_pos])

        if len(quotes_before) % 2 == 0:
            sentence = paragraph[last_end:end_pos].strip()
            combine_sentence_with_ending.append(sentence)
            last_end = end_pos

    if last_end < len(paragraph):
        combine_sentence_with_ending.append(paragraph[last_end:].strip())

    return combine_sentence_with_ending


def divide_text_into_chunks(
        text: str,
        paragraphs: list[str] = None
) -> list[str]:
    """
    Divides a large text into smaller chunks. Each chunk will contain as many paragraphs as possible.
    If a paragraph is too large, it will be divided by sentences to fit within token limits.

    :param text: The input text to be chunked.
    :param paragraphs: (Optional) List of paragraphs from the text. If not provided, they will be extracted.
    :return: A list of chunks where each chunk is a portion of the text that fits within the token limit.
    """
    tokens = count_tokens(text)

    if tokens < MAX_TOKENS:
        return [text]

    count_of_chunking = ceil(tokens / MAX_TOKENS)

    chunks = []
    if not paragraphs:
        paragraphs = divide_into_paragraphs(text)

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)

        if paragraph_tokens < MAX_TOKENS:
            # If the paragraph fits within the token limit, attempt to add it to the current chunk
            if chunks and count_tokens(chunks[-1]) + paragraph_tokens < MAX_TOKENS:
                chunks[-1] += paragraph
            else:
                chunks.append(paragraph)  # Start a new chunk with the paragraph
            continue

        # If the paragraph is too large, split it into sentences
        sentences = divide_into_sentences(paragraph)
        sentences_per_chunk = ceil(len(sentences) / count_of_chunking)

        for start in range(0, len(sentences), sentences_per_chunk):
            end = min(len(sentences), start + sentences_per_chunk)
            chunks.append("".join(sentences[start: end]))

    return chunks


async def divide_text_into_words(
        text: str,
        paragraphs: list[str] = None
) -> list:
    """
    Extract individual words from each chunk of text.
    This function utilizes the OpenAI API to process text and extract words concurrently from specified chunks.
    It is designed to enhance performance by handling requests in parallel, allowing for efficient word extraction
    from larger text inputs.
    """
    chunks = divide_text_into_chunks(text, paragraphs)
    tasks = []

    for chunk in chunks:
        # Create a coroutine for each chunk to ask OpenAI
        tasks.append(ask_openai(system_to_retrieve_words, chunk))

    # Run all tasks concurrently and gather results
    responses = await asyncio.gather(*tasks)

    words = []
    for response in responses:
        words.extend(json.loads(response))

    return words
