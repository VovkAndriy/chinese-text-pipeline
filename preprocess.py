import re
import json

from config import (
    system_to_retrieve_words,
)
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


# It divides sentence into chunks with 10% overlapping before and after chunk
# returns array of that chunks
def divide_sentence_into_chunks_with_overlapping(sentence: str) -> list:
    tokens = count_tokens(sentence)

    if tokens < MAX_TOKENS:
        return [sentence]

    count_of_chunking = ceil(tokens * 1.3 / MAX_TOKENS)
    chunk_size = int(len(sentence) / count_of_chunking)

    chunks = []
    for i in range(count_of_chunking):
        start = i * chunk_size
        end = (i + 1) * chunk_size
        part_of_sentence = sentence[start:end]

        overlapped_before, overlapped_after = "", ""

        if i != 0:
            overlapped_before = f"{sentence[ceil(start - chunk_size * 0.1):start]}"

        if i != count_of_chunking:
            overlapped_after = f"{sentence[end:ceil(end + chunk_size * 0.1)]}"

        part_of_sentence = overlapped_before + part_of_sentence + overlapped_after

        chunks.append(part_of_sentence)

    return chunks


# If sentence exceeds context window
# it will make little overlap to have context for translation
def divide_into_words(sentence: str) -> list:
    """
    Function to extract individual words from each chunk of the text.
    Specifics: Usage of an OpenAI
    """
    chunks = divide_sentence_into_chunks_with_overlapping(sentence)

    words = []
    for chunk in chunks:
        new_words = json.loads(
           ask_openai(system_to_retrieve_words, chunk)
        )

        for i in range(1, len(new_words)):
            if new_words[:i] == words[-i:]:
                new_words = new_words[i:]
                break

        words.extend(new_words)

    return words


def create_default_json(text: str):
    """Create structure for JSON"""
    return {
        "content": {
            "fullText": text,
            "fullTranslation": None,
            "paragraphs": []
        }
    }


def create_paragraph_json(id: int, paragraph: str):
    """Create structure for paragraph in JSON"""
    return {
            "id": id,
            "text": paragraph,
            "translation": None,
            "pinyin": None,
            "sentences": []
        }


def create_sentence_json(id: int, sentence: str):
    """Create structure for sentence in JSON"""
    return {
            "id": id,
            "text": sentence,
            "translation": None,
            "words": []
        }


def create_word_json(id: int, word: str):
    """Create structure for word in JSON"""
    return {
        "text": word,
        "index": id,
        "pinyin": None,
        "partOfSpeech": None,
        "translation": None
    }


def create_json_from_text(text: str):
    """
    Converts the processed words into a structured JSON format,
    currently without translation.
    """
    result_dictionary = create_default_json(text)

    paragraphs = divide_into_paragraphs(text)

    for i, paragraph in enumerate(paragraphs):
        paragraph_json = create_paragraph_json(i, paragraph)

        sentences = divide_into_sentences(paragraph)

        for j, sentence in enumerate(sentences):
            sentence_json = create_sentence_json(j, sentence)

            words = divide_into_words(sentence)

            for k, word in enumerate(words):
                word_json = create_word_json(k, word)
                sentence_json["words"].append(word_json)

            paragraph_json["sentences"].append(sentence_json)

        result_dictionary["content"]["paragraphs"].append(paragraph_json)

    return result_dictionary
