from fastapi import FastAPI, UploadFile, File
import pytesseract
from pdf2image import convert_from_path
import re
from PIL import Image
import io

app = FastAPI(
    title="Bill Extraction API",
    description="Extract line items, subtotal, final total from bills",
    version="1.0.0"
)

# --------------------------
# Utility: OCR for images
# --------------------------
def ocr_image(image: Image.Image):
    return pytesseract.image_to_string(image)

# --------------------------
# Extract line items
# --------------------------
def extract_line_items(text):
    line_items = []

    # Regex to match common invoice line structures:
    # Example: ItemName  Qty  Price  Amount
    pattern = r"([A-Za-z0-9\- ]+)\s+(\d+)\s+([\d,.]+)\s+([\d,.]+)"

    for match in re.findall(pattern, text):
        item = {
            "description": match[0].strip(),
            "quantity": int(match[1]),
            "price": float(match[2].replace(",", "")),
            "amount": float(match[3].replace(",", ""))
        }
        line_items.append(item)

    return line_items

# --------------------------
# Extract totals
# --------------------------
def extract_totals(text):
    subtotal = None
    total = None

    subt_pattern = r"Sub[\-\s]*Total[:\s]+([\d,.]+)"
    total_pattern = r"Total[:\s]+([\d,.]+)"

    subt_match = re.search(subt_pattern, text, re.IGNORECASE)
    total_match = re.search(total_pattern, text, re.IGNORECASE)

    if subt_match:
        subtotal = float(subt_match.group(1).replace(",", ""))

    if total_match:
        total = float(total_match.group(1).replace(",", ""))

    return subtotal, total

# --------------------------
# API: Upload Invoice
# --------------------------
@app.post("/extract")
async def extract_bill(file: UploadFile = File(...)):
    content = await file.read()

    # Case 1: PDF file
    if file.filename.lower().endswith(".pdf"):
        images = convert_from_path(io.BytesIO(content))
        text = ""
        for img in images:
            text += ocr_image(img) + "\n"

    else:
        # Case 2: Image file (JPG/PNG)
        image = Image.open(io.BytesIO(content))
        text = ocr_image(image)

    # Extract data
    line_items = extract_line_items(text)
    subtotal, total = extract_totals(text)

    # Calculate final total if missing
    if not total:
        total = sum(item["amount"] for item in line_items)

    return {
        "line_items": line_items,
        "subtotal": subtotal,
        "final_total": total,
        "rawText": text
    }

# --------------------------
# Root URL
# --------------------------
@app.get("/")
async def root():
    return {"message": "Bill Extraction API is running"}
