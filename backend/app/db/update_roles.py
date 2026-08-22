import asyncio
from app.db.database import get_mongo_db, init_db

async def main():
    await init_db()
    db = get_mongo_db()
    res = await db.users.update_many(
        {"email": {"$ne": "admin@intelliparse.ai"}},
        {"$set": {"role": "analyst"}}
    )
    print(f"Updated {res.modified_count} users to role 'analyst'.")

if __name__ == "__main__":
    asyncio.run(main())
