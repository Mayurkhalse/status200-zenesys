import asyncio
from app.db.database import get_mongo_db, init_db

async def main():
    await init_db()
    db = get_mongo_db()
    cursor = db.documents.find({}).sort("created_at", -1).limit(5)
    async for d in cursor:
        print(f"ID: {d['_id']} | Status: {d['status']} | UploadedBy: {d['uploaded_by']} | Error: {d.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
