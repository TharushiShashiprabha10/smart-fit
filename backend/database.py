from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection URL (ඔබේ ප්‍රොජෙක්ට් එකේ පාවිච්චි කරන URL එක මෙහි ඇත)
MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)


database = client.smartfit_db



users_collection = database.get_collection("users")
products_collection = database.get_collection("products")
measurements_collection = database.get_collection("measurements")