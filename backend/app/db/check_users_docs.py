import asyncio
from app.db.database import get_mongo_db, init_db

async def main():
    await init_db()
    db = get_mongo_db()

    users = await db.users.find({}).to_list(20)
    print("=== USERS IN MONGO ===")
    for u in users:
        print(f"User ID: {u['_id']} | Email: {u['email']} | Role: {u.get('role')}")

    docs = await db.documents.find({}).to_list(20)
    print("\n=== DOCUMENTS IN MONGO ===")
    for d in docs:
        print(f"Doc ID: {d['_id']} | UploadedBy: {d.get('uploaded_by')} | Filename: {d.get('original_filename')}")

if __name__ == "__main__":
    asyncio.run(main())
