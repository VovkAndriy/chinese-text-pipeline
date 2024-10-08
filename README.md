# Chinese Text Processing Pipeline

This pipeline processes Chinese text by breaking it into paragraphs, sentences, and words, with support for handling long sentences using chunking and overlapping to ensure context is preserved.

## Setup Instructions

### 1. Install Dependencies
To install the necessary dependencies, run the following command:
```bash
pip install -r requirements.txt
```

### 2. Create .env file with
```bash
OPENAI_API_KEY=<YOUR-API-KEY>
```

## What Does This Script Do?

This script processes Chinese text through a series of steps, including text division, word extraction, and JSON output generation. Below is a breakdown of each module and its functionality:

### 1. `config.py`
- Contains the prompt that defines how the system interacts with OpenAI's API for extracting individual words from sentences.

### 2. `openai_request.py`
- Provides functions to interact with OpenAI's API:
  - `ask_openai()`: Sends a request to OpenAI using the provided prompt, retrieves the word list, and handles the response.
  - `count_tokens()`: A utility function to count the number of tokens in a sentence, helping to ensure requests do not exceed OpenAI's context window.

### 3. `preprocess.py`
- Includes core functions to process the input text:
  - **Text Division:**
    - `divide_into_paragraphs()`: Splits the input text into paragraphs.
    - `divide_into_sentences()`: Further divides paragraphs into individual sentences.
  - **Chunking:**
    - `divide_text_into_chunks()`: Divides a large text into smaller chunks. Each chunk will contain as many paragraphs as possible.
    If a paragraph is too large, it will be divided by sentences to fit within token limits.
  - **Word Extraction:**
    - `divide_into_words()`: Uses OpenAI to extract individual words from each chunk of the text.

### 4. `json_creator.py`
  - **JSON Creation:**
    - `create_json_from_text()`: Converts the processed words into a structured JSON format without translation, allowing for easy further analysis or manipulation of the text.
    - other default functions like `create_paragraph_json()` for creation JSON structure

### 5.  FastAPI Endpoint
- Endpoint `POST /get-json/`
  - This endpoint receives Chinese text in the request body and returns the processed JSON output, including extracted words and their structure.
  - Be sure to handle quotes correctly! (as \")

### 4. Overall Pipeline Workflow
1. The text is split into paragraphs, then sentences.
2. To split into words it uses intelligent chunking.
2. Paragraphs that exceed OpenAI's context window are divided into smaller chunks (full sentences).
3. Each chunk is sent to OpenAI for word extraction.
4. The output, including extracted words and punctuation, is formatted into a JSON structure.
