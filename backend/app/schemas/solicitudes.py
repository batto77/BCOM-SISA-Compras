from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# ─── Mini schemas para display anidado ───────────────────────────────────────

class ProductoMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class CategoriaProductoMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    tipo: str


class ServicioMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class UnidadMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    simbolo: str


class RubroMiniOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo: Optional[str] = None


# ─── ItemSolicitud ────────────────────────────────────────────────────────────

class ItemSolicitudCreate(BaseModel):
    id: Optional[int] = None
    tipo: str  # producto/servicio/libre
    descripcion: str
    cantidad: Optional[Decimal] = Decimal("1")
    unidad_medida_id: Optional[int] = None
    producto_id: Optional[int] = None
    categoria_producto_id: Optional[int] = None
    servicio_id: Optional[int] = None
    especificaciones: Optional[str] = None
    notas: Optional[str] = None
    presupuesto_estimado: Optional[Decimal] = None
    orden: int = 0


class ItemSolicitudOut(ItemSolicitudCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    solicitud_id: int
    producto: Optional[ProductoMiniOut] = None
    categoria_producto: Optional[CategoriaProductoMiniOut] = None
    servicio: Optional[ServicioMiniOut] = None
    unidad: Optional[UnidadMiniOut] = None


# ─── SolicitudCompra ──────────────────────────────────────────────────────────

class SolicitudCompraCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    solicitante_nombre: str
    aprobador: Optional[str] = Field(default=None, max_length=200)
    rubro_id: Optional[int] = None
    rubro_ids: List[int] = Field(default_factory=list, max_length=20)
    fecha_requerida: Optional[date] = None
    prioridad: str = "medio"
    moneda: str = "COP"
    notas: Optional[str] = None
    campos_extra: Optional[dict] = None
    pesos_evaluacion: Optional[dict] = None
    items: List[ItemSolicitudCreate] = []


class SolicitudCompraUpdate(BaseModel):
    numero: Optional[str] = Field(default=None, max_length=20)
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    solicitante_nombre: Optional[str] = None
    aprobador: Optional[str] = Field(default=None, max_length=200)
    rubro_id: Optional[int] = None
    rubro_ids: Optional[List[int]] = Field(default=None, max_length=20)
    fecha_requerida: Optional[date] = None
    prioridad: Optional[str] = None
    moneda: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    campos_extra: Optional[dict] = None
    pesos_evaluacion: Optional[dict] = None
    items: Optional[List[ItemSolicitudCreate]] = None


class AdjudicadoAOut(BaseModel):
    """Proveedor al que se le adjudicaron ítems de la oportunidad."""
    cotizacion_id: int
    proveedor_id: int
    razon_social: str
    items: int


class SolicitudCompraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: Optional[str] = None
    campos_extra: Optional[dict] = None
    pesos_evaluacion: Optional[dict] = None
    titulo: str
    descripcion: Optional[str] = None
    solicitante_nombre: str
    aprobador: Optional[str] = None
    rubro_id: Optional[int] = None
    fecha_requerida: Optional[date] = None
    prioridad: str
    moneda: str = "COP"
    estado: str
    version_actual: int = 1
    notas: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    fecha_cancelacion: Optional[datetime] = None
    fecha_adjudicacion: Optional[datetime] = None
    cotizacion_ganadora_id: Optional[int] = None
    adjudicacion_items: Optional[dict] = None
    # Proveedores adjudicados, resueltos en el router (no es una columna).
    adjudicado_a: List[AdjudicadoAOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ItemSolicitudOut] = []
    rubro: Optional[RubroMiniOut] = None
    rubros: List[RubroMiniOut] = Field(default_factory=list)


class SolicitudListOut(BaseModel):
    items: List[SolicitudCompraOut]
    total: int
    skip: int
    limit: int
