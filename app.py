from fastapi import FastAPI

from services.json_creator import create_json_from_text
from models import TextRequest


app = FastAPI()


@app.post("/get-json/")
async def get_json_from_text(request: TextRequest):
    """
    Receive chinese text and return a json response.
    """
    return await create_json_from_text(request.text)
