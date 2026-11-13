from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection URL (ඔබේ ප්‍රොජෙක්ට් එකේ පාවිච්චි කරන URL එක මෙහි ඇත)
MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

# Database එකේ නම (SmartFit DB)
database = client.smartfit_db

# Collection දෙක නිවැරදිව නිර්මාණය කර Export කිරීම
users_collection = database.get_collection("users")
products_collection = database.get_collection("products")