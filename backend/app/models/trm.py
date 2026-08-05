from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Numeric, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TasaCambio(Base):
    __tablename__ = "tasas_cambio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    moneda: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    tasa_cop: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, onupdate=func.now())


class HistorialTasaCambio(Base):
    __tablename__ = "historial_tasas_cambio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    tasa_cop_anterior: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4), nullable=True)
    tasa_cop_nueva: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    usuario: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, index=True)
