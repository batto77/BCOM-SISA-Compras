from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    String, Integer, DateTime, Date, Text, ForeignKey, Numeric, func, Table, Column, Boolean
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CampoSolicitud(Base):
    """Campos dinámicos configurables para el encabezado de una oportunidad."""
    __tablename__ = "campos_solicitud"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tipo_dato: Mapped[str] = mapped_column(String(20), default="texto", nullable=False)  # texto/numero/fecha/booleano/lista
    opciones: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # para tipo lista
    obligatorio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


solicitud_rubros = Table(
    "solicitud_rubros",
    Base.metadata,
    Column(
        "solicitud_id",
        Integer,
        ForeignKey("solicitudes_compra.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "rubro_id",
        Integer,
        ForeignKey("rubros_presupuestales.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ItemSolicitud(Base):
    __tablename__ = "items_solicitud"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("solicitudes_compra.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # producto/servicio/libre
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    cantidad: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=1, nullable=True)
    unidad_medida_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("unidades_medida.id"), nullable=True
    )
    producto_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("productos.id"), nullable=True
    )
    categoria_producto_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categorias_producto.id"), nullable=True
    )
    servicio_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("servicios.id"), nullable=True
    )
    especificaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    presupuesto_estimado: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relaciones
    solicitud: Mapped["SolicitudCompra"] = relationship(
        "SolicitudCompra", back_populates="items"
    )
    producto: Mapped[Optional["Producto"]] = relationship(  # type: ignore[name-defined]
        "Producto", lazy="joined"
    )
    categoria_producto: Mapped[Optional["CategoriaProducto"]] = relationship(  # type: ignore[name-defined]
        "CategoriaProducto", lazy="joined"
    )
    servicio: Mapped[Optional["Servicio"]] = relationship(  # type: ignore[name-defined]
        "Servicio", lazy="joined"
    )
    unidad: Mapped[Optional["UnidadMedida"]] = relationship(  # type: ignore[name-defined]
        "UnidadMedida", lazy="joined"
    )


class SolicitudCompra(Base):
    __tablename__ = "solicitudes_compra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solicitante_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    aprobador: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    rubro_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("rubros_presupuestales.id"), nullable=True
    )
    fecha_requerida: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    prioridad: Mapped[str] = mapped_column(
        String(20), default="medio", nullable=False
    )  # critico/alto/medio/bajo — según el impacto en la operación
    # (valores anteriores urgente/alta/normal/baja migrados en main.py)
    moneda: Mapped[str] = mapped_column(
        String(3), default="COP", nullable=False
    )  # COP, USD, EUR, etc.
    estado: Mapped[str] = mapped_column(
        String(30), default="borrador", nullable=False
    )  # borrador/enviada/en_cotizacion/adjudicada/rechazada/cancelada
    # ('aprobada' quedó obsoleto: el cierre del flujo ahora es 'adjudicada'.
    #  Se conserva en registros históricos y se sigue mostrando en la UI.)
    # Motivo obligatorio al cancelar la oportunidad.
    motivo_cancelacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_cancelacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_adjudicacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    version_actual: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    campos_extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # {campo_id: valor}
    # Pesos de los criterios de evaluación para esta oportunidad (override de los base).
    # Ej: {"financiero": 40, "calificacion": 10, "tiempo_entrega": 30, "completitud": 20}
    pesos_evaluacion: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Cotización seleccionada como ganadora (caso "todo a un proveedor") + justificación.
    cotizacion_ganadora_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    justificacion_seleccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Adjudicación por ítem (la compra puede repartirse): {item_solicitud_id: cotizacion_id}
    adjudicacion_items: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    rubro: Mapped[Optional["RubroPresupuestal"]] = relationship(  # type: ignore[name-defined]
        "RubroPresupuestal", lazy="joined"
    )
    rubros: Mapped[List["RubroPresupuestal"]] = relationship(  # type: ignore[name-defined]
        "RubroPresupuestal",
        secondary=solicitud_rubros,
        lazy="selectin",
        order_by="RubroPresupuestal.nombre",
    )
    items: Mapped[List["ItemSolicitud"]] = relationship(
        "ItemSolicitud",
        back_populates="solicitud",
        cascade="all, delete-orphan",
        order_by="ItemSolicitud.orden",
    )
