from services.preprocess import (
    divide_into_paragraphs,
    divide_text_into_words,
    divide_into_sentences
)


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


async def create_json_from_text(text: str):
    """
    Converts the passed text into a structured JSON format,
    currently without translation.
    """
    result_dictionary = create_default_json(text)

    paragraphs = divide_into_paragraphs(text)

    words = await divide_text_into_words(text, paragraphs)
    words_index = 0

    for i, paragraph in enumerate(paragraphs):
        paragraph_json = create_paragraph_json(i, paragraph)

        sentences = divide_into_sentences(paragraph)

        for j, sentence in enumerate(sentences):
            sentence_json = create_sentence_json(j, sentence)
            accumulated_length = 0

            for k in range(words_index, len(words)):
                word = words[k]
                accumulated_length += len(word)
                word_json = create_word_json(k - words_index, word)
                sentence_json["words"].append(word_json)

                if accumulated_length >= len(sentence):
                    words_index = k + 1
                    break

            paragraph_json["sentences"].append(sentence_json)

        result_dictionary["content"]["paragraphs"].append(paragraph_json)

    return result_dictionary
