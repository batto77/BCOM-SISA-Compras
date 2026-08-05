from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Boolean, Integer, DateTime, ForeignKey, Text, Table, Column, Numeric, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# Tabla de asociación N:M proveedor ↔ etiqueta
proveedor_etiquetas = Table(
    "proveedor_etiquetas",
    Base.metadata,
    Column("proveedor_id", Integer, ForeignKey("proveedores.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)


class Proveedor(Base):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    tipo_persona: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # juridica/natural
    monedas: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # ["COP","USD","EUR"]
    moneda_defecto: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)  # COP/USD/EUR
    calificacion: Mapped[Optional[float]] = mapped_column(Numeric(3, 1), nullable=True)  # 0.0 – 10.0 (estrellas)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_comercial: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    pais: Mapped[str] = mapped_column(String(100), nullable=False)
    idioma: Mapped[str] = mapped_column(String(2), default="ES", nullable=False)
    sitio_web: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    contactos: Mapped[List["ContactoProveedor"]] = relationship(
        "ContactoProveedor", back_populates="proveedor", cascade="all, delete-orphan"
    )
    etiquetas: Mapped[List["Etiqueta"]] = relationship(  # type: ignore[name-defined]
        "Etiqueta", secondary=proveedor_etiquetas
    )


class ContactoProveedor(Base):
    __tablename__ = "contactos_proveedor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proveedor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("proveedores.id", ondelete="CASCADE"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    cargo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    proveedor: Mapped["Proveedor"] = relationship(
        "Proveedor", back_populates="contactos"
    )
    emails: Mapped[List["EmailContacto"]] = relationship(
        "EmailContacto", back_populates="contacto", cascade="all, delete-orphan"
    )
    telefonos: Mapped[List["TelefonoContacto"]] = relationship(
        "TelefonoContacto", back_populates="contacto", cascade="all, delete-orphan"
    )


class EmailContacto(Base):
    __tablename__ = "emails_contacto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contacto_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contactos_proveedor.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), default="comercial", nullable=False)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contacto: Mapped["ContactoProveedor"] = relationship(
        "ContactoProveedor", back_populates="emails"
    )


class TelefonoContacto(Base):
    __tablename__ = "telefonos_contacto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contacto_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contactos_proveedor.id", ondelete="CASCADE"),
        nullable=False,
    )
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), default="celular", nullable=False)
    extension: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    contacto: Mapped["ContactoProveedor"] = relationship(
        "ContactoProveedor", back_populates="telefonos"
    )
