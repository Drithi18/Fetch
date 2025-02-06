from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator, constr
from uuid import uuid4
from datetime import datetime, time
import math
import re

app = FastAPI()

# In-memory storage
receipts = {}

# Models
class Item(BaseModel):
    shortDescription: constr(pattern=r"^[\w\s\-]+$")
    price: constr(pattern=r"^\d+\.\d{2}$")

    @validator("price")
    def validate_price(cls, v):
        if float(v) <= 0:
            raise ValueError("Price must be positive")
        return v

class Receipt(BaseModel):
    retailer: constr(pattern=r"^[\w\s\-&]+$")
    purchaseDate: str
    purchaseTime: str
    items: list[Item]
    total: constr(pattern=r"^\d+\.\d{2}$")

    @validator("purchaseDate")
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

    @validator("purchaseTime")
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM (24h)")
        return v

    @validator("items")
    def validate_items(cls, v):
        if len(v) < 1:
            raise ValueError("At least one item required")
        return v

# Endpoints
@app.post("/receipts/process")
async def process_receipt(receipt: Receipt):
    receipt_id = str(uuid4())
    receipts[receipt_id] = receipt.dict()
    return {"id": receipt_id}

@app.get("/receipts/{id}/points")
async def get_points(id: str):
    receipt = receipts.get(id)
    if not receipt:
        raise HTTPException(status_code=404, detail="No receipt found for that ID")
    
    points = 0
    
    # Rule 1: Alphanumeric chars in retailer name
    points += len(re.sub(r"[^\w]", "", receipt["retailer"]))
    
    # Rule 2: Round dollar amount
    if float(receipt["total"]).is_integer():
        points += 50
    
    # Rule 3: Multiple of 0.25
    if (float(receipt["total"]) * 100) % 25 == 0:
        points += 25
    
    # Rule 4: 5 points per two items
    points += (len(receipt["items"]) // 2) * 5
    
    # Rule 5: Item description length multiple of 3
    for item in receipt["items"]:
        desc_length = len(item["shortDescription"].strip())
        if desc_length % 3 == 0:
            price = float(item["price"])
            points += math.ceil(price * 0.2)
    
    # Rule 6: Odd purchase day
    purchase_date = datetime.strptime(receipt["purchaseDate"], "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6
    
    # Rule 7: Purchase time between 2:00pm and 4:00pm
    purchase_time = datetime.strptime(receipt["purchaseTime"], "%H:%M").time()
    if time(14, 0) <= purchase_time <= time(16, 0):
        points += 10
    
    return {"points": points}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)