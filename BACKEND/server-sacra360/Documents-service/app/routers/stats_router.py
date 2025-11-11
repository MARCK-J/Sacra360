"""
Router de estadísticas y reportes
Endpoint: /stats/dashboard
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.models import Sacramento as SacramentoModel

router = APIRouter()


@router.get("/stats/dashboard")
def dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    total_documents = db.query(SacramentoModel).count()
    # For this minimal dashboard, processed_documents equals total_documents
    processed_documents = total_documents

    # documents_by_type and by_month
    docs_by_type = {}
    docs = db.query(SacramentoModel.tipo_sacramento, func.count(SacramentoModel.id)).group_by(SacramentoModel.tipo_sacramento).all()
    for tipo, cnt in docs:
        docs_by_type[tipo] = cnt

    data = {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "processing_pipeline": {
            "ocr_pending": 0,
            "htr_pending": 0,
            "ai_pending": 0
        },
        "documents_by_type": docs_by_type,
        "documents_by_status": {},
        "documents_by_month": {},
        "last_updated": now
    }

    return data
