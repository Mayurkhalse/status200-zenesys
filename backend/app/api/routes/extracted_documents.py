from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, require_roles, UserSession
from app.core.encryption import encryption_service
from app.services.pii_service import pii_service
from app.services.audit_service import audit_service
from app.models.schemas.extracted import ExtractedDocumentItem, UpdateExtractedDocumentRequest

router = APIRouter(prefix="/extracted-documents", tags=["Extracted Documents"])

@router.get("/{document_id}", response_model=ExtractedDocumentItem)
async def get_extracted_document(document_id: str, current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()

    # Check parent document ownership
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and str(doc["uploaded_by"]) != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to view this document")

    extracted = await db.extracted_documents.find_one({"document_id": ObjectId(document_id)})
    if not extracted:
        raise HTTPException(status_code=404, detail="Extracted document record not found")

    # Decrypt fields
    fields = encryption_service.decrypt_field(extracted["fields"]) if isinstance(extracted["fields"], str) else extracted["fields"]

    # Remap PII tokens if user is admin or analyst
    if doc and doc.get("pii_redaction_map_ref") and current_user.role in ["admin", "analyst"]:
        redaction_map = encryption_service.decrypt_field(doc["pii_redaction_map_ref"])
        if redaction_map:
            fields = pii_service.remap_pii(fields, redaction_map)

    return ExtractedDocumentItem(
        id=str(extracted["_id"]),
        document_id=str(extracted["document_id"]),
        document_type=extracted["document_type"],
        fields=fields or {},
        field_confidences=extracted.get("field_confidences", {}),
        needs_review=extracted.get("needs_review", False),
        extraction_source=extracted.get("extraction_source", "hybrid"),
        reviewed_by=str(extracted.get("reviewed_by")) if extracted.get("reviewed_by") else None,
        reviewed_at=extracted.get("reviewed_at"),
        created_at=extracted["created_at"],
        updated_at=extracted["updated_at"]
    )

@router.patch("/{document_id}", response_model=ExtractedDocumentItem)
async def update_extracted_document(
    document_id: str,
    req: UpdateExtractedDocumentRequest,
    current_user: UserSession = Depends(require_roles(["admin", "analyst"]))
):
    db = get_mongo_db()

    # Check parent document ownership
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and str(doc["uploaded_by"]) != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to modify this document")

    # Re-encrypt fields
    encrypted_fields = encryption_service.encrypt_field(req.fields)

    now = datetime.now(timezone.utc)
    update_dict = {
        "fields": encrypted_fields,
        "needs_review": False,
        "reviewed_by": ObjectId(current_user.user_id),
        "reviewed_at": now,
        "updated_at": now
    }

    await db.extracted_documents.update_one({"document_id": ObjectId(document_id)}, {"$set": update_dict})
    await db.documents.update_one({"_id": ObjectId(document_id)}, {"$set": {"status": "completed"}})

    await audit_service.log_action(
        current_user.user_id,
        "edit",
        "extracted_document",
        document_id,
        detail={"updated_fields": list(req.fields.keys())}
    )

    updated = await db.extracted_documents.find_one({"document_id": ObjectId(document_id)})
    return ExtractedDocumentItem(
        id=str(updated["_id"]),
        document_id=str(updated["document_id"]),
        document_type=updated["document_type"],
        fields=req.fields,
        field_confidences=updated.get("field_confidences", {}),
        needs_review=False,
        extraction_source=updated.get("extraction_source", "hybrid"),
        reviewed_by=current_user.user_id,
        reviewed_at=now,
        created_at=updated["created_at"],
        updated_at=now
    )
