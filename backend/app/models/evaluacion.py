from sqlalchemy import String, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CriterioEvaluacion(Base):
    """Tabla paramétrica de criterios para la selección del proveedor ganador.

    Los pesos base (peso_default) son el punto de partida; cada oportunidad
    puede sobrescribirlos en solicitudes_compra.pesos_evaluacion (JSONB).
    """
    __tablename__ = "criterios_evaluacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    clave: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)  # financiero/calificacion/tiempo_entrega/completitud
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=True)
    peso_default: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)  # % (0-100)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
