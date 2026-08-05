from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.etiquetas import EtiquetaOut
from app.schemas.parametros import UnidadMedidaOut


# --- CategoriaProducto ---

class CategoriaProductoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=30)
    icono: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class CategoriaProductoCreate(CategoriaProductoBase):
    slug: Optional[str] = Field(default=None, max_length=100)


class CategoriaProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    tipo: Optional[str] = Field(None, max_length=30)
    icono: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class CategoriaProductoOut(CategoriaProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoriaProductoListOut(BaseModel):
    items: List[CategoriaProductoOut]
    total: int
    skip: int
    limit: int


# --- DefinicionCampo ---

class DefinicionCampoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    clave: str = Field(..., max_length=50)
    orden: int = 0
    tipo_dato: str = Field(..., max_length=20)
    es_obligatorio: bool = False
    es_campo_base: bool = True
    tiene_cantidad: bool = False
    tiene_unidad: bool = False
    unidad_default_id: Optional[int] = None
    placeholder: Optional[str] = Field(None, max_length=255)
    descripcion_ayuda: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class DefinicionCampoCreate(DefinicionCampoBase):
    opciones_unidad_ids: List[int] = []


class DefinicionCampoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    clave: Optional[str] = Field(None, max_length=50)
    orden: Optional[int] = None
    tipo_dato: Optional[str] = Field(None, max_length=20)
    es_obligatorio: Optional[bool] = None
    tiene_cantidad: Optional[bool] = None
    tiene_unidad: Optional[bool] = None
    unidad_default_id: Optional[int] = None
    placeholder: Optional[str] = Field(None, max_length=255)
    descripcion_ayuda: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class DefinicionCampoOut(DefinicionCampoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria_producto_id: int
    unidad_default: Optional[UnidadMedidaOut] = None
    opciones_unidad: List[UnidadMedidaOut] = []


class DefinicionCampoListOut(BaseModel):
    items: List[DefinicionCampoOut]
    total: int
    skip: int
    limit: int


class AsignarUnidadesRequest(BaseModel):
    unidad_ids: List[int]


# --- ValorEspecificacion ---

class ValorEspecificacionBase(BaseModel):
    campo_id: int
    cantidad: Optional[Decimal] = None
    valor: Optional[str] = Field(None, max_length=500)
    unidad_medida_id: Optional[int] = None


class ValorEspecificacionCreate(ValorEspecificacionBase):
    pass


class ValorEspecificacionOut(ValorEspecificacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    campo: Optional[DefinicionCampoOut] = None
    unidad_medida: Optional[UnidadMedidaOut] = None


class EspecificacionesBatchRequest(BaseModel):
    especificaciones: List[ValorEspecificacionBase]


# --- ModeloProducto ---

class ModeloProductoBase(BaseModel):
    fabricante: str = Field(..., max_length=100)
    modelo: str = Field(..., max_length=200)
    es_primario: bool = False
    orden: int = 0


class ModeloProductoCreate(ModeloProductoBase):
    pass


class ModeloProductoOut(ModeloProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int


# --- Producto ---

class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    categoria_producto_id: int
    modo_defecto: str = Field(default="funcional", max_length=25)
    fabricante: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    activo: bool = True


class ProductoCreate(ProductoBase):
    etiqueta_ids: List[int] = []
    especificaciones: List[ValorEspecificacionBase] = []


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    categoria_producto_id: Optional[int] = None
    modo_defecto: Optional[str] = Field(None, max_length=25)
    fabricante: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None
    etiqueta_ids: Optional[List[int]] = None


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    especificaciones: List[ValorEspecificacionOut] = []
    modelos_alternativos: List[ModeloProductoOut] = []
    etiquetas: List[EtiquetaOut] = []


class ProductoListOut(BaseModel):
    items: List[ProductoOut]
    total: int
    skip: int
    limit: int


# --- CategoriaServicio ---

class CategoriaServicioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class CategoriaServicioCreate(CategoriaServicioBase):
    pass


class CategoriaServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class CategoriaServicioOut(CategoriaServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoriaServicioListOut(BaseModel):
    items: List[CategoriaServicioOut]
    total: int
    skip: int
    limit: int


# --- Servicio ---

class ServicioBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    categoria_servicio_id: Optional[int] = None
    tipo_servicio_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    activo: bool = True


class ServicioCreate(ServicioBase):
    etiqueta_ids: List[int] = []


class ServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    categoria_servicio_id: Optional[int] = None
    tipo_servicio_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    activo: Optional[bool] = None
    etiqueta_ids: Optional[List[int]] = None


class ServicioOut(ServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    etiquetas: List[EtiquetaOut] = []
    unidad_medida: Optional[UnidadMedidaOut] = None


class ServicioListOut(BaseModel):
    items: List[ServicioOut]
    total: int
    skip: int
    limit: int
