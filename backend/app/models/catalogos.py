from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Boolean, Integer, DateTime, ForeignKey, Text, Table, Column,
    Numeric, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# Tabla de asociación DefinicionCampo ↔ UnidadMedida (opciones disponibles)
campo_unidades = Table(
    "campo_unidades",
    Base.metadata,
    Column("campo_id", Integer, ForeignKey("definiciones_campo.id"), primary_key=True),
    Column(
        "unidad_medida_id",
        Integer,
        ForeignKey("unidades_medida.id"),
        primary_key=True,
    ),
)

# Tabla de asociación Producto ↔ Etiqueta
producto_etiquetas = Table(
    "producto_etiquetas",
    Base.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)

# Tabla de asociación Servicio ↔ Etiqueta
servicio_etiquetas = Table(
    "servicio_etiquetas",
    Base.metadata,
    Column("servicio_id", Integer, ForeignKey("servicios.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)


class CategoriaProducto(Base):
    __tablename__ = "categorias_producto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    icono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    campos: Mapped[List["DefinicionCampo"]] = relationship(
        "DefinicionCampo",
        back_populates="categoria_producto",
        order_by="DefinicionCampo.orden",
    )
    productos: Mapped[List["Producto"]] = relationship(
        "Producto", back_populates="categoria_producto"
    )


class DefinicionCampo(Base):
    __tablename__ = "definiciones_campo"

    __table_args__ = (
        UniqueConstraint("categoria_producto_id", "clave", name="uq_campo_categoria_clave"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    categoria_producto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categorias_producto.id"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    clave: Mapped[str] = mapped_column(String(50), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tipo_dato: Mapped[str] = mapped_column(String(20), nullable=False)
    es_obligatorio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_campo_base: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tiene_cantidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tiene_unidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unidad_default_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("unidades_medida.id"), nullable=True
    )
    placeholder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    descripcion_ayuda: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria_producto: Mapped["CategoriaProducto"] = relationship(
        "CategoriaProducto", back_populates="campos"
    )
    unidad_default: Mapped[Optional["UnidadMedida"]] = relationship(  # type: ignore[name-defined]
        "UnidadMedida", foreign_keys=[unidad_default_id]
    )
    opciones_unidad: Mapped[List["UnidadMedida"]] = relationship(  # type: ignore[name-defined]
        "UnidadMedida", secondary=campo_unidades
    )


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categoria_producto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categorias_producto.id"), nullable=False
    )
    modo_defecto: Mapped[str] = mapped_column(
        String(25), default="funcional", nullable=False
    )
    fabricante: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    categoria_producto: Mapped["CategoriaProducto"] = relationship(
        "CategoriaProducto", back_populates="productos"
    )
    especificaciones: Mapped[List["ValorEspecificacion"]] = relationship(
        "ValorEspecificacion",
        back_populates="producto",
        cascade="all, delete-orphan",
    )
    modelos_alternativos: Mapped[List["ModeloProducto"]] = relationship(
        "ModeloProducto",
        back_populates="producto",
        cascade="all, delete-orphan",
        order_by="ModeloProducto.orden",
    )
    etiquetas: Mapped[List["Etiqueta"]] = relationship(  # type: ignore[name-defined]
        "Etiqueta", secondary=producto_etiquetas
    )


class ValorEspecificacion(Base):
    __tablename__ = "valores_especificacion"

    __table_args__ = (
        UniqueConstraint("producto_id", "campo_id", name="uq_especificacion_producto_campo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    producto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False
    )
    campo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("definiciones_campo.id"), nullable=False
    )
    cantidad: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    valor: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    unidad_medida_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("unidades_medida.id"), nullable=True
    )

    producto: Mapped["Producto"] = relationship(
        "Producto", back_populates="especificaciones"
    )
    campo: Mapped["DefinicionCampo"] = relationship("DefinicionCampo")
    unidad_medida: Mapped[Optional["UnidadMedida"]] = relationship(  # type: ignore[name-defined]
        "UnidadMedida"
    )


class ModeloProducto(Base):
    __tablename__ = "modelos_producto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    producto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False
    )
    fabricante: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(200), nullable=False)
    es_primario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    producto: Mapped["Producto"] = relationship(
        "Producto", back_populates="modelos_alternativos"
    )


class CategoriaServicio(Base):
    __tablename__ = "categorias_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    servicios: Mapped[List["Servicio"]] = relationship(
        "Servicio", back_populates="categoria_servicio"
    )


class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categoria_servicio_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categorias_servicio.id"), nullable=True
    )
    tipo_servicio_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tipos_servicio.id"), nullable=True
    )
    unidad_medida_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("unidades_medida.id"), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    categoria_servicio: Mapped[Optional["CategoriaServicio"]] = relationship(
        "CategoriaServicio", back_populates="servicios"
    )
    tipo_servicio: Mapped[Optional["TipoServicio"]] = relationship(  # type: ignore[name-defined]
        "TipoServicio"
    )
    unidad_medida: Mapped[Optional["UnidadMedida"]] = relationship(  # type: ignore[name-defined]
        "UnidadMedida"
    )
    etiquetas: Mapped[List["Etiqueta"]] = relationship(  # type: ignore[name-defined]
        "Etiqueta", secondary=servicio_etiquetas
    )
