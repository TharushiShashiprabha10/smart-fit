from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import users_collection, products_collection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Products ලබාගැනීමේ API එක
@app.get("/api/products")
async def get_products():
    products = []
    async for product in products_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return {"status": "success", "data": products}

# 2. Smart Size Recommendation සඳහා අවශ්‍ය Request Model එක
class SmartSizeRequest(BaseModel):
    height: float
    weight: float
    body_shape: str
    fit_preference: str

# 3. Size Recommendation API එක (මෙන්න මේක තියෙන්නම ඕන!)
@app.post("/api/recommend-size")
async def recommend_size(data: SmartSizeRequest):
    base_chest = data.weight * 1.3 + (data.height * 0.1)
    base_waist = data.weight * 1.1 + (data.height * 0.08)

    if data.body_shape.lower() == "hourglass":
        chest = base_chest + 2
        waist = base_waist - 4
    elif data.body_shape.lower() == "pear":
        chest = base_chest - 2
        waist = base_waist
    elif data.body_shape.lower() == "athletic":
        chest = base_chest + 4
        waist = base_waist + 2
    else:
        chest = base_chest
        waist = base_waist

    if chest < 82 and waist < 68:
        base_size = "S"
    elif 82 <= chest <= 94 and 68 <= waist <= 78:
        base_size = "M"
    elif 94 < chest <= 104 and 78 <= waist <= 88:
        base_size = "L"
    else:
        base_size = "XL"

    final_size = base_size
    sizes_order = ["S", "M", "L", "XL"]
    
    if data.fit_preference.lower() == "loose":
        current_index = sizes_order.index(base_size)
        if current_index < len(sizes_order) - 1:
            final_size = sizes_order[current_index + 1]

    return {
        "status": "success",
        "estimated_chest": round(chest, 1),
        "estimated_waist": round(waist, 1),
        "recommended_size": final_size,
        "message": f"Based on your {data.body_shape} body shape and {data.fit_preference} fit preference, your estimated measurements (Chest: {round(chest,1)}cm) give a perfect match of size {final_size}!"
    }

    class SmartSizeRequest(BaseModel):
    height: float
    weight: float
    body_shape: str
    fit_preference: str
    category: str = "General"