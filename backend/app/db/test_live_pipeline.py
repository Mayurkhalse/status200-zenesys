import asyncio
from app.db.database import init_db, get_mongo_db
from app.api.routes.documents import process_document_pipeline

async def main():
    await init_db()
    db = get_mongo_db()

    # Test 1: Upload Purchase Order
    po_doc = await db.documents.insert_one({
        "original_filename": "sample_po.txt",
        "mime_type": "text/plain",
        "status": "uploaded",
        "uploaded_by": "test_user_01"
    })
    po_id = str(po_doc.inserted_id)
    po_content = b"PURCHASE ORDER\nPO Number: PO-9912\nVendor: Global Logistics LLC\nBuyer: Acme Corp\nTotal: $4500.00"
    
    await process_document_pipeline(po_id, po_content, "sample_po.txt", "text/plain", "test_user_01")
    po_res = await db.documents.find_one({"_id": po_doc.inserted_id})
    
    # Test 2: Upload Lead Inquiry
    lead_doc = await db.documents.insert_one({
        "original_filename": "inquiry_lead.txt",
        "mime_type": "text/plain",
        "status": "uploaded",
        "uploaded_by": "test_user_01"
    })
    lead_id = str(lead_doc.inserted_id)
    lead_content = b"CRM LEAD INQUIRY\nContact Name: Sarah Connor\nCompany: Cyberdyne Systems\nBudget: $50,000"
    
    await process_document_pipeline(lead_id, lead_content, "inquiry_lead.txt", "text/plain", "test_user_01")
    lead_res = await db.documents.find_one({"_id": lead_doc.inserted_id})

    print("=== LIVE PIPELINE TEST RESULTS ===")
    print(f"PO Doc Classification: {po_res.get('classification', {}).get('document_type')} | Status: {po_res.get('status')}")
    print(f"Lead Doc Classification: {lead_res.get('classification', {}).get('document_type')} | Status: {lead_res.get('status')}")

if __name__ == "__main__":
    asyncio.run(main())
