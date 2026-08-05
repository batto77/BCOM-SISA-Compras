from typing import Optional

from sqlalchemy import String, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UnidadMedida(Base):
    __tablename__ = "unidades_medida"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    simbolo: Mapped[str] = mapped_column(String(10), nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RubroPresupuestal(Base):
    __tablename__ = "rubros_presupuestales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    monto_max_auto_aprobacion: Mapped[Optional[float]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NivelAprobacion(Base):
    __tablename__ = "niveles_aprobacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    monto_max: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    delegable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class PlantillaANS(Base):
    __tablename__ = "plantillas_ans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    horas: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class TipoServicio(Base):
    __tablename__ = "tipos_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
