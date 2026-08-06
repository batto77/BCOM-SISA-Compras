"""Generador de números DAV automáticos (AAAA-NNNNN)."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.solicitudes import SolicitudCompra


def generar_proximo_dav(db: Session) -> str:
    """
    Genera el próximo número DAV con estructura AAAA-NNNNN.
    - AAAA: año en curso
    - NNNNN: secuencial que empieza en 00000 e incrementa en 1

    Ej: 2026-00001, 2026-00002, ..., 2026-99999
    """
    anio_actual = datetime.now().year
    prefijo = f"{anio_actual}-"

    # Buscar el último DAV de este año
    ultimo_dav = (
        db.query(SolicitudCompra)
        .filter(SolicitudCompra.numero.like(f"{prefijo}%"))
        .order_by(SolicitudCompra.numero.desc())
        .first()
    )

    if ultimo_dav and ultimo_dav.numero:
        # Extraer el número secuencial y incrementar
        partes = ultimo_dav.numero.split("-")
        if len(partes) == 2:
            try:
                secuencial = int(partes[1])
                siguiente = secuencial + 1
            except (ValueError, IndexError):
                siguiente = 1
        else:
            siguiente = 1
    else:
        siguiente = 1

    # Formatear con 5 dígitos (00001, 00002, etc.)
    return f"{prefijo}{siguiente:05d}"
