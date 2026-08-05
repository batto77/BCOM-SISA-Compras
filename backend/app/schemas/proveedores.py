from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.schemas.etiquetas import EtiquetaOut


# --- EmailContacto ---

class EmailContactoBase(BaseModel):
    email: EmailStr
    tipo: str = Field(default="comercial", max_length=30)
    es_principal: bool = False


class EmailContactoCreate(EmailContactoBase):
    pass


class EmailContactoUpdate(BaseModel):
    email: Optional[EmailStr] = None
    tipo: Optional[str] = Field(None, max_length=30)
    es_principal: Optional[bool] = None


class EmailContactoOut(EmailContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contacto_id: int


# --- TelefonoContacto ---

class TelefonoContactoBase(BaseModel):
    numero: str = Field(..., max_length=50)
    tipo: str = Field(default="celular", max_length=20)
    extension: Optional[str] = Field(None, max_length=10)


class TelefonoContactoCreate(TelefonoContactoBase):
    pass


class TelefonoContactoUpdate(BaseModel):
    numero: Optional[str] = Field(None, max_length=50)
    tipo: Optional[str] = Field(None, max_length=20)
    extension: Optional[str] = Field(None, max_length=10)


class TelefonoContactoOut(TelefonoContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contacto_id: int


# --- ContactoProveedor ---

class ContactoProveedorBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    cargo: Optional[str] = Field(None, max_length=100)
    es_principal: bool = False
    activo: bool = True


class ContactoProveedorCreate(ContactoProveedorBase):
    pass


class ContactoProveedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    cargo: Optional[str] = Field(None, max_length=100)
    es_principal: Optional[bool] = None
    activo: Optional[bool] = None


class ContactoProveedorOut(ContactoProveedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proveedor_id: int
    emails: List[EmailContactoOut] = []
    telefonos: List[TelefonoContactoOut] = []


# --- Schemas embebidos para crear/actualizar contactos anidados en el proveedor ---

class EmailContactoEmbedded(BaseModel):
    """Email dentro del payload del formulario de proveedor (id opcional = nuevo)."""
    id: Optional[int] = None
    email: EmailStr
    tipo: str = Field(default="comercial", max_length=30)
    es_principal: bool = False


class TelefonoContactoEmbedded(BaseModel):
    """Teléfono dentro del payload del formulario de proveedor (id opcional = nuevo)."""
    id: Optional[int] = None
    numero: str = Field(..., max_length=50)
    tipo: str = Field(default="celular", max_length=20)
    extension: Optional[str] = Field(None, max_length=10)


class ContactoProveedorEmbedded(BaseModel):
    """Contacto dentro del payload del formulario de proveedor (id opcional = nuevo)."""
    id: Optional[int] = None
    nombre: str = Field(..., max_length=200)
    cargo: Optional[str] = Field(None, max_length=100)
    es_principal: bool = False
    activo: bool = True
    emails: List[EmailContactoEmbedded] = []
    telefonos: List[TelefonoContactoEmbedded] = []


# --- Proveedor ---

class ProveedorBase(BaseModel):
    nit: Optional[str] = Field(None, max_length=30)
    tipo_persona: Optional[str] = Field(None, max_length=20)  # juridica/natural
    monedas: Optional[List[str]] = None  # ["COP","USD","EUR"]
    moneda_defecto: Optional[str] = Field(None, max_length=3)  # COP/USD/EUR
    calificacion: Optional[float] = Field(None, ge=0, le=10)  # 0-10 estrellas
    razon_social: str = Field(..., max_length=200)
    nombre_comercial: Optional[str] = Field(None, max_length=200)
    pais: str = Field(..., max_length=100)
    idioma: str = Field(default="ES", max_length=2)
    sitio_web: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    estado: str = Field(default="activo", max_length=20)


class ProveedorCreate(ProveedorBase):
    etiqueta_ids: List[int] = []
    contactos: List[ContactoProveedorEmbedded] = []


class ProveedorUpdate(BaseModel):
    nit: Optional[str] = Field(None, max_length=30)
    tipo_persona: Optional[str] = Field(None, max_length=20)
    monedas: Optional[List[str]] = None
    moneda_defecto: Optional[str] = Field(None, max_length=3)
    calificacion: Optional[float] = Field(None, ge=0, le=10)
    razon_social: Optional[str] = Field(None, max_length=200)
    nombre_comercial: Optional[str] = Field(None, max_length=200)
    pais: Optional[str] = Field(None, max_length=100)
    idioma: Optional[str] = Field(None, max_length=2)
    sitio_web: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=20)
    etiqueta_ids: Optional[List[int]] = None
    contactos: Optional[List[ContactoProveedorEmbedded]] = None


class ProveedorOut(ProveedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    contactos: List[ContactoProveedorOut] = []
    etiquetas: List[EtiquetaOut] = []


class ProveedorListOut(BaseModel):
    items: List[ProveedorOut]
    total: int
    skip: int
    limit: int
