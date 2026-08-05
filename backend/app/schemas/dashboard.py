from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class OportunidadRecienteOut(BaseModel):
    id: int
    numero: Optional[str] = None
    titulo: str
    estado: str
    prioridad: str
    fecha_requerida: Optional[date] = None
    created_at: datetime
    proveedores_invitados: int = 0
    respuestas_recibidas: int = 0


class DashboardResumenOut(BaseModel):
    oportunidades_activas: int = 0
    cotizaciones_pendientes: int = 0
    cotizaciones_respondidas: int = 0
    proveedores_activos: int = 0
    tasa_respuesta: float = Field(default=0, ge=0, le=100)
    oportunidades_por_estado: Dict[str, int]
    oportunidades_recientes: List[OportunidadRecienteOut]
