from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- UnidadMedida ---

class UnidadMedidaBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    simbolo: str = Field(..., max_length=10)
    categoria: Optional[str] = Field(None, max_length=50)
    activo: bool = True


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    simbolo: Optional[str] = Field(None, max_length=10)
    categoria: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class UnidadMedidaOut(UnidadMedidaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UnidadMedidaListOut(BaseModel):
    items: List[UnidadMedidaOut]
    total: int
    skip: int
    limit: int


# --- RubroPresupuestal ---

class RubroPresupuestalBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)
    monto_max_auto_aprobacion: Optional[Decimal] = None
    activo: bool = True


class RubroPresupuestalCreate(RubroPresupuestalBase):
    pass


class RubroPresupuestalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)
    monto_max_auto_aprobacion: Optional[Decimal] = None
    activo: Optional[bool] = None


class RubroPresupuestalOut(RubroPresupuestalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RubroPresupuestalListOut(BaseModel):
    items: List[RubroPresupuestalOut]
    total: int
    skip: int
    limit: int


# --- NivelAprobacion ---

class NivelAprobacionBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    monto_max: Optional[Decimal] = None
    delegable: bool = True
    orden: int = 0


class NivelAprobacionCreate(NivelAprobacionBase):
    pass


class NivelAprobacionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    monto_max: Optional[Decimal] = None
    delegable: Optional[bool] = None
    orden: Optional[int] = None


class NivelAprobacionOut(NivelAprobacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class NivelAprobacionListOut(BaseModel):
    items: List[NivelAprobacionOut]
    total: int
    skip: int
    limit: int


# --- PlantillaANS ---

class PlantillaANSBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    horas: int
    descripcion: Optional[str] = Field(None, max_length=255)


class PlantillaANSCreate(PlantillaANSBase):
    pass


class PlantillaANSUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    horas: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=255)


class PlantillaANSOut(PlantillaANSBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PlantillaANSListOut(BaseModel):
    items: List[PlantillaANSOut]
    total: int
    skip: int
    limit: int


# --- TipoServicio ---

class TipoServicioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class TipoServicioCreate(TipoServicioBase):
    pass


class TipoServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class TipoServicioOut(TipoServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TipoServicioListOut(BaseModel):
    items: List[TipoServicioOut]
    total: int
    skip: int
    limit: int
