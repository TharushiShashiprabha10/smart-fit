from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from database import users_collection, products_collection, measurements_collection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/products")
async def get_products():
    products = []
    async for product in products_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return {"status": "success", "data": products}


class SmartSizeRequest(BaseModel):
    height: float
    weight: float
    body_shape: str
    fit_preference: str
    category: str = "General"


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

    record = {
        "category": data.category,
        "height": data.height,
        "weight": data.weight,
        "body_shape": data.body_shape,
        "fit_preference": data.fit_preference,
        "estimated_chest": round(chest, 1),
        "estimated_waist": round(waist, 1),
        "recommended_size": final_size,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    await measurements_collection.insert_one(record)

    return {
        "status": "success",
        "estimated_chest": round(chest, 1),
        "estimated_waist": round(waist, 1),
        "recommended_size": final_size,
        "message": f"Based on your {data.body_shape} body shape and {data.fit_preference} fit preference, your estimated measurements (Chest: {round(chest,1)}cm) give a perfect match of size {final_size}!"
    }


@app.get("/api/measurements")
async def get_measurements():
    records = []
    async for item in measurements_collection.find():
        item["_id"] = str(item["_id"])
        records.append(item)
    return {"status": "success", "data": records}


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/register")
async def register_user(data: RegisterRequest):
    existing_user = await users_collection.find_one({"email": data.email.strip()})
    if existing_user:
        return {"error": "Email already registered!"}

    user_dict = {
        "username": data.username.strip(),
        "email": data.email.strip(),
        "password": data.password.strip()
    }

    await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully!"}


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
async def login_user(data: LoginRequest):
    user = await users_collection.find_one({"email": data.email.strip()})

    if not user:
        return {"error": "Email not found!"}

    if user["password"].strip() != data.password.strip():
        return {"error": "Incorrect password!"}

    return {"message": "Login Successful!"}


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


@app.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    user = await users_collection.find_one({"email": data.email.strip()})
    if not user:
        return {"error": "Email not found!"}

    await users_collection.update_one(
        {"email": data.email.strip()},
        {"$set": {"password": data.new_password.strip()}}
    )
    return {"message": "Password updated successfully!"}