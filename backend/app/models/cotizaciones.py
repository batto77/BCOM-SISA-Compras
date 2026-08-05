from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    String, Integer, DateTime, Date, Text, ForeignKey, Numeric, Boolean, func,
    UniqueConstraint, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ItemCotizacion(Base):
    __tablename__ = "items_cotizacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cotizacion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cotizaciones.id", ondelete="CASCADE"), nullable=False
    )
    item_solicitud_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("items_solicitud.id"), nullable=True
    )
    precio_unitario: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    tiempo_entrega_dias: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valores_especificacion: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ficha_tecnica_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    moneda: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relaciones
    cotizacion: Mapped["Cotizacion"] = relationship(
        "Cotizacion", back_populates="items"
    )
    item_solicitud: Mapped[Optional["ItemSolicitud"]] = relationship(  # type: ignore[name-defined]
        "ItemSolicitud", lazy="joined"
    )


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("solicitudes_compra.id", ondelete="CASCADE"), nullable=False
    )
    proveedor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("proveedores.id"), nullable=False
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="invitada", nullable=False
    )  # invitada/respondida/descartada
    version_actual: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    respuesta_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_limite_respuesta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas_internas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notas_proveedor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_cotizacion_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    solicitud: Mapped["SolicitudCompra"] = relationship(  # type: ignore[name-defined]
        "SolicitudCompra", lazy="joined"
    )
    proveedor: Mapped["Proveedor"] = relationship(  # type: ignore[name-defined]
        "Proveedor", lazy="joined"
    )
    items: Mapped[List["ItemCotizacion"]] = relationship(
        "ItemCotizacion",
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="ItemCotizacion.orden",
    )
    versiones: Mapped[List["CotizacionVersion"]] = relationship(
        "CotizacionVersion",
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="CotizacionVersion.numero_version",
    )


class CotizacionVersion(Base):
    __tablename__ = "cotizaciones_versiones"
    __table_args__ = (
        UniqueConstraint(
            "cotizacion_id",
            "numero_version",
            name="uq_cotizacion_version_numero",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cotizacion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cotizaciones.id", ondelete="CASCADE"), nullable=False
    )
    numero_version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    cotizacion: Mapped["Cotizacion"] = relationship(
        "Cotizacion", back_populates="versiones"
    )
