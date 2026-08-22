import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query, status
from bson import ObjectId

from app.core.config import settings
from app.core.rbac import get_current_user, require_roles, UserSession
from app.core.encryption import encryption_service
from app.db.database import get_mongo_db
from app.models.schemas.documents import DocumentItem, DocumentListResponse, DocumentStatusResponse
from app.services.ocr_service import ocr_service
from app.services.classification_service import classification_service
from app.services.extraction_service import extraction_service
from app.services.pii_service import pii_service
from app.services.audit_service import audit_service
from app.agents.insights.insight_agent import insight_agent
from app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/png",
    "image/jpeg"
]

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserSession = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_FILE_TYPE", "message": f"Unsupported MIME type: {file.content_type}", "detail": None}}
        )

    file_bytes = await file.read()
    if len(file_bytes) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": "File exceeds max 25MB limit", "detail": None}}
        )

    # 1. Encrypt file immediately on upload
    encrypted_file_bytes = encryption_service.encrypt_bytes(file_bytes)

    doc_id = ObjectId()
    doc_id_str = str(doc_id)

    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{doc_id_str}.enc")

    with open(file_path, "wb") as f:
        f.write(encrypted_file_bytes)

    # 2. Create document record in MongoDB
    db = get_mongo_db()
    doc_record = {
        "_id": doc_id,
        "filename": f"{doc_id_str}.enc",
        "original_filename": file.filename,
        "mime_type": file.content_type,
        "file_size_bytes": len(file_bytes),
        "storage_path": file_path,
        "status": "uploaded",
        "classification": None,
        "pii_redaction_map_ref": None,
        "uploaded_by": ObjectId(current_user.user_id),
        "error": None,
        "retry_count": 0,
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    await db.documents.insert_one(doc_record)
    await audit_service.log_action(current_user.user_id, "upload", "document", doc_id_str)

    # 3. Queue background processing pipeline
    background_tasks.add_task(process_document_pipeline, doc_id_str, file_bytes, file.filename, file.content_type, current_user.user_id)

    return {"document_id": doc_id_str, "status": "uploaded"}

async def process_document_pipeline(document_id: str, file_bytes: bytes, filename: str, mime_type: str, user_id: str):
    db = get_mongo_db()
    doc_oid = ObjectId(document_id)

    try:
        # Step 1: Preprocessing & OCR
        await db.documents.update_one({"_id": doc_oid}, {"$set": {"status": "preprocessing"}})
        ocr_result = ocr_service.extract_text_from_bytes(file_bytes, mime_type, filename)
        raw_text = ocr_result.get("text", "")

        # Step 2: Classification
        await db.documents.update_one({"_id": doc_oid}, {"$set": {"status": "classifying"}})
        class_res = await classification_service.classify_document(raw_text, filename)

        await db.documents.update_one(
            {"_id": doc_oid},
            {"$set": {"classification": class_res, "status": "extracting"}}
        )

        # Step 3: PII Redaction
        redacted_text, redaction_map = pii_service.redact_pii(raw_text)
        encrypted_redaction_map = encryption_service.encrypt_field(redaction_map)

        await db.documents.update_one(
            {"_id": doc_oid},
            {"$set": {"pii_redaction_map_ref": encrypted_redaction_map}}
        )

        # Step 4: Specialized Extraction
        doc_type = class_res["document_type"]
        extracted_fields, confidences, needs_review = await extraction_service.extract_fields(doc_type, redacted_text)

        # Encrypt sensitive fields before writing to MongoDB
        encrypted_fields = encryption_service.encrypt_field(extracted_fields)

        extracted_doc_record = {
            "document_id": doc_oid,
            "document_type": doc_type,
            "fields": encrypted_fields,
            "field_confidences": confidences,
            "needs_review": needs_review or (class_res["decision"] == "HUMAN_REVIEW"),
            "extraction_source": class_res["source"],
            "reviewed_by": None,
            "reviewed_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.extracted_documents.replace_one({"document_id": doc_oid}, extracted_doc_record, upsert=True)

        # Step 5: Sync with ERP records (source: pipeline)
        party_name = extracted_fields.get("vendor") or extracted_fields.get("customer") or extracted_fields.get("client") or extracted_fields.get("lead_name") or "Unknown Party"
        total_amount = extracted_fields.get("total") or extracted_fields.get("amount") or extracted_fields.get("estimated_value") or 0.0

        erp_record = {
            "record_type": doc_type,
            "source": "pipeline",
            "linked_document_id": doc_oid,
            "party_name": str(party_name),
            "amount": float(total_amount) if total_amount else None,
            "currency": extracted_fields.get("currency", "USD"),
            "key_dates": {
                "issue_date": extracted_fields.get("issue_date") or extracted_fields.get("order_date"),
                "due_date": extracted_fields.get("due_date") or extracted_fields.get("delivery_date")
            },
            "erp_status": "draft",
            "status_history": [{
                "status": "draft",
                "changed_by": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
                "changed_at": datetime.now(timezone.utc)
            }],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.erp_records.insert_one(erp_record)

        # Step 6: Insight Generation
        await db.documents.update_one({"_id": doc_oid}, {"$set": {"status": "insight_pending"}})
        
        # History context lookup
        history_cursor = db.erp_records.find({"party_name": party_name}).sort("created_at", -1).limit(10)
        history = [h async for h in history_cursor]

        insights = await insight_agent.generate_insights(
            doc_type, extracted_fields, party_name, history, {"record_count": len(history)}
        )

        for ins in insights:
            insight_doc = {
                "type": ins["type"],
                "severity": ins["severity"],
                "title": ins["title"],
                "description": ins["description"],
                "related_entity": ins["related_entity"],
                "related_document_ids": [doc_oid],
                "status": "open",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.insights.insert_one(insight_doc)

        # Step 7: Index for RAG search
        await retrieval_service.index_document(document_id, redacted_text)

        # Final Status
        final_status = "human_review" if (needs_review or class_res["decision"] == "HUMAN_REVIEW") else "completed"
        await db.documents.update_one(
            {"_id": doc_oid},
            {"$set": {"status": final_status, "updated_at": datetime.now(timezone.utc)}}
        )

    except Exception as e:
        print(f"Pipeline error for document {document_id}: {e}")
        await db.documents.update_one(
            {"_id": doc_oid},
            {"$set": {
                "status": "failed",
                "error": {"code": "PIPELINE_FAILED", "message": str(e), "stage": "pipeline"}
            }}
        )

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserSession = Depends(get_current_user)
):
    db = get_mongo_db()
    query = {"is_deleted": False}

    # Non-admin users only see documents they uploaded
    if current_user.role != "admin":
        user_id_val = ObjectId(current_user.user_id) if ObjectId.is_valid(current_user.user_id) else current_user.user_id
        query["uploaded_by"] = user_id_val

    if status:
        query["status"] = status
    if document_type:
        query["classification.document_type"] = document_type

    total = await db.documents.count_documents(query)
    cursor = db.documents.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)

    items = []
    async for doc in cursor:
        items.append(DocumentItem(
            document_id=str(doc["_id"]),
            filename=doc["filename"],
            original_filename=doc["original_filename"],
            mime_type=doc["mime_type"],
            file_size_bytes=doc["file_size_bytes"],
            status=doc["status"],
            classification=doc.get("classification"),
            uploaded_by=str(doc["uploaded_by"]),
            error=doc.get("error"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        ))

    return DocumentListResponse(items=items, total=total, page=page, limit=limit)

@router.get("/{document_id}", response_model=DocumentItem)
async def get_document(document_id: str, current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    doc = await db.documents.find_one({"_id": ObjectId(document_id), "is_deleted": False})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Access control check
    if current_user.role != "admin" and str(doc["uploaded_by"]) != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to view this document")

    return DocumentItem(
        document_id=str(doc["_id"]),
        filename=doc["filename"],
        original_filename=doc["original_filename"],
        mime_type=doc["mime_type"],
        file_size_bytes=doc["file_size_bytes"],
        status=doc["status"],
        classification=doc.get("classification"),
        uploaded_by=str(doc["uploaded_by"]),
        error=doc.get("error"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str, current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if current_user.role != "admin" and str(doc["uploaded_by"]) != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    decision = doc.get("classification", {}).get("decision") if doc.get("classification") else None
    return DocumentStatusResponse(
        status=doc["status"],
        decision=decision,
        error=doc.get("error")
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, current_user: UserSession = Depends(require_roles(["admin"]))):
    db = get_mongo_db()
    res = await db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"is_deleted": True, "deleted_at": datetime.now(timezone.utc)}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    await audit_service.log_action(current_user.user_id, "delete", "document", document_id)
    return None
