"""
Router público — sin autenticación.
Usado por los proveedores para ver y responder cotizaciones a través del link único.
"""
import os
import shutil
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.cotizaciones import crud_cotizacion
from app.models.trm import TasaCambio

router = APIRouter(prefix="/public")

UPLOADS_DIR = "/app/uploads"


# ─── Schemas públicos (sin datos sensibles internos) ─────────────────────────

class ItemSolicitudPublicoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
    descripcion: str
    cantidad: Optional[Decimal] = None
    categoria_producto_id: Optional[int] = None
    especificaciones: Optional[str] = None
    notas: Optional[str] = None


class ItemCotizacionPublicoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_solicitud_id: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    tiempo_entrega_dias: Optional[int] = None
    garantia_meses: Optional[int] = None
    disponible: bool
    notas: Optional[str] = None
    orden: int
    ficha_tecnica_path: Optional[str] = None
    ficha_tecnica_url: Optional[str] = None
    moneda: Optional[str] = None
    item_solicitud: Optional[ItemSolicitudPublicoOut] = None

    @model_validator(mode='after')
    def _compute_url(self) -> 'ItemCotizacionPublicoOut':
        if self.ficha_tecnica_path:
            self.ficha_tecnica_url = f"/uploads/{self.ficha_tecnica_path}"
        return self


class TasaCambioPublicoOut(BaseModel):
    moneda: str
    tasa_cop: Decimal


class CotizacionPublicaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    token: Optional[str] = None
    estado: str
    version_actual: int = 1
    respuesta_version: Optional[int] = None
    fecha_limite_respuesta: Optional[object] = None
    notas_proveedor: Optional[str] = None
    pdf_cotizacion_url: Optional[str] = None
    # Info de la solicitud
    solicitud_titulo: str = ""
    solicitud_numero: Optional[str] = None
    solicitud_prioridad: str = ""
    solicitud_fecha_requerida: Optional[object] = None
    # Estado de la oportunidad: si está adjudicada o cancelada el proveedor ya no
    # puede modificar nada y debe ver el aviso correspondiente.
    solicitud_estado: str = ""
    solicitud_motivo_cancelacion: Optional[str] = None
    cerrada: bool = False
    # Adjudicación: si a este proveedor le adjudicaron ítems, se listan para que ejecute.
    fue_adjudicado: bool = False
    items_adjudicados_ids: List[int] = []
    # Info del proveedor
    proveedor_nombre: str = ""
    proveedor_monedas: List[str] = []
    proveedor_moneda_defecto: Optional[str] = None
    # Tasas de cambio vigentes
    tasas_cambio: List[TasaCambioPublicoOut] = []
    # Items a cotizar
    items: List[ItemCotizacionPublicoOut] = []


class ItemRespuestaProveedor(BaseModel):
    item_cotizacion_id: int
    precio_unitario: Optional[Decimal] = None
    tiempo_entrega_dias: Optional[int] = None
    garantia_meses: Optional[int] = None  # 0 = no aplica
    disponible: bool = True
    notas: Optional[str] = None
    moneda: Optional[str] = None


class RespuestaProveedorIn(BaseModel):
    items: List[ItemRespuestaProveedor]
    notas_proveedor: Optional[str] = None


class UploadOut(BaseModel):
    url: str
    nombre: str


# ─── Helpers ─────────────────────────────────────────────────────────────────

ESTADOS_CERRADOS = ("adjudicada", "cancelada")


def _items_adjudicados_a(cot, sol) -> List[int]:
    """IDs de items_solicitud que le fueron adjudicados a ESTA cotización."""
    if not sol or not sol.adjudicacion_items:
        return []
    return [
        int(item_id)
        for item_id, cot_id in sol.adjudicacion_items.items()
        if cot_id == cot.id
    ]


def _build_out(cot, db: Session) -> CotizacionPublicaOut:
    sol = cot.solicitud
    prov = cot.proveedor
    pdf_url = f"/uploads/{cot.pdf_cotizacion_path}" if cot.pdf_cotizacion_path else None
    tasas = db.query(TasaCambio).order_by(TasaCambio.moneda).all()
    estado_sol = sol.estado if sol else ""
    adjudicados = _items_adjudicados_a(cot, sol) if estado_sol == "adjudicada" else []
    return CotizacionPublicaOut(
        id=cot.id,
        token=cot.token,
        estado=cot.estado,
        version_actual=cot.version_actual,
        respuesta_version=cot.respuesta_version,
        fecha_limite_respuesta=cot.fecha_limite_respuesta,
        notas_proveedor=cot.notas_proveedor,
        pdf_cotizacion_url=pdf_url,
        solicitud_titulo=sol.titulo if sol else "",
        solicitud_numero=sol.numero if sol else None,
        solicitud_prioridad=sol.prioridad if sol else "",
        solicitud_fecha_requerida=sol.fecha_requerida if sol else None,
        solicitud_estado=estado_sol,
        solicitud_motivo_cancelacion=(sol.motivo_cancelacion if sol else None),
        cerrada=estado_sol in ESTADOS_CERRADOS,
        fue_adjudicado=bool(adjudicados),
        items_adjudicados_ids=adjudicados,
        proveedor_nombre=prov.razon_social if prov else "",
        proveedor_monedas=list(prov.monedas or []) if prov else [],
        proveedor_moneda_defecto=prov.moneda_defecto if prov else None,
        tasas_cambio=[TasaCambioPublicoOut(moneda=t.moneda, tasa_cop=t.tasa_cop) for t in tasas],
        items=cot.items,
    )


def _validate_token(token: str, db: Session):
    cot = crud_cotizacion.get_by_token(db, token=token)
    if not cot:
        raise HTTPException(status_code=404, detail="Link de cotización no válido o expirado.")
    if cot.estado == "descartada":
        raise HTTPException(status_code=410, detail="Esta cotización ha sido descartada.")
    return cot


def _bloquear_si_cerrada(cot) -> None:
    """Impide cualquier modificación si la oportunidad ya fue adjudicada o cancelada.

    La UI oculta los controles, pero el link es público: el candado real va acá.
    """
    sol = cot.solicitud
    estado = sol.estado if sol else ""
    if estado == "adjudicada":
        raise HTTPException(
            status_code=409,
            detail="Esta oportunidad ya fue adjudicada. No se admiten más cambios.",
        )
    if estado == "cancelada":
        raise HTTPException(
            status_code=409,
            detail="Esta oportunidad fue cancelada. No se admiten más cambios.",
        )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/cotizar/{token}", response_model=CotizacionPublicaOut)
def obtener_cotizacion_publica(token: str, db: Session = Depends(get_db)):
    cot = _validate_token(token, db)
    return _build_out(cot, db)


@router.post("/cotizar/{token}/responder", response_model=CotizacionPublicaOut)
def responder_cotizacion(
    token: str,
    data: RespuestaProveedorIn,
    db: Session = Depends(get_db),
):
    cot = _validate_token(token, db)
    _bloquear_si_cerrada(cot)
    items_map = {item.id: item for item in cot.items}

    for resp in data.items:
        item = items_map.get(resp.item_cotizacion_id)
        if item:
            item.precio_unitario = resp.precio_unitario
            item.tiempo_entrega_dias = resp.tiempo_entrega_dias
            item.garantia_meses = resp.garantia_meses or 0
            item.disponible = resp.disponible
            item.notas = resp.notas
            if resp.moneda:
                item.moneda = resp.moneda.upper()

    cot.notas_proveedor = data.notas_proveedor
    cot.estado = "respondida"
    cot.respuesta_version = cot.version_actual
    cot.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(cot)
    crud_cotizacion._ensure_version_snapshot(db, cotizacion=cot)
    db.commit()
    db.refresh(cot)

    return _build_out(cot, db)


@router.post("/cotizar/{token}/upload-item/{item_cotizacion_id}", response_model=UploadOut)
async def subir_ficha_tecnica(
    token: str,
    item_cotizacion_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """El proveedor sube la ficha técnica PDF de un ítem específico."""
    cot = _validate_token(token, db)
    _bloquear_si_cerrada(cot)

    item = next((i for i in cot.items if i.id == item_cotizacion_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado.")

    ext = (file.filename or "").lower().split(".")[-1]
    if ext != "pdf" and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF.")

    subdir = os.path.join(UPLOADS_DIR, "cotizaciones", token)
    os.makedirs(subdir, exist_ok=True)
    filename = f"item_{item_cotizacion_id}_ficha.pdf"
    filepath = os.path.join(subdir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    item.ficha_tecnica_path = f"cotizaciones/{token}/{filename}"
    db.commit()

    return UploadOut(url=f"/uploads/cotizaciones/{token}/{filename}", nombre=file.filename or filename)


@router.post("/cotizar/{token}/upload-pdf", response_model=UploadOut)
async def subir_pdf_cotizacion(
    token: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """El proveedor sube un PDF general de su cotización."""
    cot = _validate_token(token, db)
    _bloquear_si_cerrada(cot)

    ext = (file.filename or "").lower().split(".")[-1]
    if ext != "pdf" and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF.")

    subdir = os.path.join(UPLOADS_DIR, "cotizaciones", token)
    os.makedirs(subdir, exist_ok=True)
    filename = "cotizacion_general.pdf"
    filepath = os.path.join(subdir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    cot.pdf_cotizacion_path = f"cotizaciones/{token}/{filename}"
    db.commit()

    return UploadOut(url=f"/uploads/cotizaciones/{token}/{filename}", nombre=file.filename or filename)
