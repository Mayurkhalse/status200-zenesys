from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db.database import get_mongo_db

class AuditService:
    async def log_action(
        self,
        user_id: Optional[str],
        action: str,  # upload | edit | erp_write | delete | login | logout | register
        resource_type: str,  # document | extracted_document | erp_record | insight | user
        resource_id: str,
        detail: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        db = get_mongo_db()
        doc = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id),
            "detail": detail,
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc)
        }
        await db.audit_logs.insert_one(doc)

audit_service = AuditService()
