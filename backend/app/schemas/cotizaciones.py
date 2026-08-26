from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Optional, List

from pydantic import BaseModel, ConfigDict, Field


# ─── Mini schemas para display anidado ───────────────────────────────────────

class SolicitudMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: Optional[str] = None
    titulo: str
    solicitante_nombre: str
    estado: str
    prioridad: str
    fecha_requerida: Optional[date] = None
    version_actual: int = 1


class ProveedorMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str
    nombre_comercial: Optional[str] = None
    pais: str
    calificacion: Optional[float] = None


class ItemSolicitudMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    descripcion: str
    cantidad: Optional[Decimal] = None
    unidad_medida_id: Optional[int] = None
    categoria_producto_id: Optional[int] = None
    especificaciones: Optional[str] = None
    notas: Optional[str] = None


# ─── ItemCotizacion ───────────────────────────────────────────────────────────

class ItemCotizacionCreate(BaseModel):
    item_solicitud_id: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    tiempo_entrega_dias: Optional[int] = None
    garantia_meses: Optional[int] = None
    disponible: bool = True
    notas: Optional[str] = None
    valores_especificacion: Optional[dict] = None
    orden: int = 0


class ItemCotizacionUpdate(BaseModel):
    item_solicitud_id: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    tiempo_entrega_dias: Optional[int] = None
    garantia_meses: Optional[int] = None
    disponible: Optional[bool] = None
    notas: Optional[str] = None
    orden: Optional[int] = None


class ItemCotizacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cotizacion_id: int
    item_solicitud_id: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    tiempo_entrega_dias: Optional[int] = None
    garantia_meses: Optional[int] = None
    disponible: bool
    notas: Optional[str] = None
    valores_especificacion: Optional[dict] = None
    orden: int
    item_solicitud: Optional[ItemSolicitudMiniOut] = None


# ─── Cotizacion ───────────────────────────────────────────────────────────────

class CotizacionCreate(BaseModel):
    solicitud_id: int
    proveedor_id: int
    fecha_limite_respuesta: Optional[date] = None
    notas_internas: Optional[str] = None
    items: List[ItemCotizacionCreate] = []


class CotizacionUpdate(BaseModel):
    estado: Optional[str] = None
    notas_internas: Optional[str] = None
    notas_proveedor: Optional[str] = None
    fecha_limite_respuesta: Optional[date] = None
    items: Optional[List[ItemCotizacionCreate]] = None


class CotizacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token: Optional[str] = None
    solicitud_id: int
    proveedor_id: int
    estado: str
    version_actual: int = 1
    respuesta_version: Optional[int] = None
    fecha_limite_respuesta: Optional[date] = None
    notas_internas: Optional[str] = None
    notas_proveedor: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ItemCotizacionOut] = []
    solicitud: Optional[SolicitudMiniOut] = None
    proveedor: Optional[ProveedorMiniOut] = None
    # Derivado de la adjudicación de la oportunidad (la compra puede repartirse).
    adjudicada: bool = False
    items_adjudicados: int = 0


class CotizacionListOut(BaseModel):
    items: List[CotizacionOut]
    total: int
    skip: int
    limit: int


# ─── Schema especial para enviar RFQ a múltiples proveedores ─────────────────

class EnviarRFQRequest(BaseModel):
    solicitud_id: int
    proveedor_ids: List[int]
    asignaciones: Dict[int, List[int]] = Field(default_factory=dict)
    fecha_limite_respuesta: Optional[date] = None
    notas_internas: Optional[str] = None
