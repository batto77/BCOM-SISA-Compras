from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auditoria import AuditLog

router = APIRouter()

TABLAS_LABELS = {
    "solicitudes_compra": "Oportunidades",
    "cotizaciones": "Cotizaciones",
    "proveedores": "Proveedores",
    "categorias_producto": "Catálogo — Categorías",
    "campos_definicion": "Catálogo — Campos",
    "etiquetas": "Etiquetas",
    "rubros_presupuestales": "Parámetros — Rubros",
}


@router.get("/auditoria", summary="Log de auditoría del sistema")
def listar_auditoria(
    tabla: Optional[str] = None,
    accion: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if tabla:
        query = query.filter(AuditLog.tabla == tabla)
    if accion:
        query = query.filter(AuditLog.accion == accion)
    if desde:
        try:
            query = query.filter(AuditLog.created_at >= datetime.fromisoformat(desde))
        except ValueError:
            pass
    if hasta:
        try:
            query = query.filter(AuditLog.created_at <= datetime.fromisoformat(hasta))
        except ValueError:
            pass

    total = query.count()
    registros = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": r.id,
                "tabla": r.tabla,
                "tabla_label": TABLAS_LABELS.get(r.tabla, r.tabla),
                "registro_id": r.registro_id,
                "accion": r.accion,
                "usuario": r.usuario,
                "descripcion": r.descripcion,
                "datos_nuevos": r.datos_nuevos,
                "datos_anteriores": r.datos_anteriores,
                "created_at": r.created_at.isoformat(),
            }
            for r in registros
        ],
    }
