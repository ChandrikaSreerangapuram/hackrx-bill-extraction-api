from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class RequestModel(BaseModel):
    document: str

@app.post("/extract-bill-data")
async def extract_bill_data(payload: RequestModel):
    # Call your OCR + LLM pipeline here
    # For now, dummy structure template:
    return {
        "is_success": True,
        "token_usage": {
            "total_tokens": 100,
            "input_tokens": 50,
            "output_tokens": 50
        },
        "data": {
            "pagewise_line_items": [
                {
                    "page_no": "1",
                    "page_type": "Bill Detail",
                    "bill_items": []
                }
            ],
            "total_item_count": 0
        }
    }
