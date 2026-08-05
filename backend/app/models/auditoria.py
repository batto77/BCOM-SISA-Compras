from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tabla: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    registro_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    accion: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # create/update/delete
    usuario: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    datos_nuevos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    datos_anteriores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False, index=True
    )
