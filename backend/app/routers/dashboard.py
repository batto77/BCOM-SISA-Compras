from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cotizaciones import Cotizacion
from app.models.proveedores import Proveedor
from app.models.solicitudes import SolicitudCompra
from app.schemas.dashboard import DashboardResumenOut, OportunidadRecienteOut

router = APIRouter()

ESTADOS_OPORTUNIDAD_ACTIVA = ("borrador", "enviada", "en_cotizacion")


@router.get("/dashboard/resumen", response_model=DashboardResumenOut)
def obtener_resumen_dashboard(db: Session = Depends(get_db)) -> DashboardResumenOut:
    """Retorna métricas operativas agregadas para el dashboard interno."""
    oportunidades_activas = (
        db.query(func.count(SolicitudCompra.id))
        .filter(SolicitudCompra.estado.in_(ESTADOS_OPORTUNIDAD_ACTIVA))
        .scalar()
        or 0
    )
    cotizaciones_pendientes = (
        db.query(func.count(Cotizacion.id))
        .filter(Cotizacion.estado == "invitada")
        .scalar()
        or 0
    )
    cotizaciones_respondidas = (
        db.query(func.count(Cotizacion.id))
        .filter(Cotizacion.estado == "respondida")
        .scalar()
        or 0
    )
    proveedores_activos = (
        db.query(func.count(Proveedor.id))
        .filter(Proveedor.estado == "activo")
        .scalar()
        or 0
    )

    estados = {
        estado: cantidad
        for estado, cantidad in (
            db.query(SolicitudCompra.estado, func.count(SolicitudCompra.id))
            .group_by(SolicitudCompra.estado)
            .all()
        )
    }

    conteos_cotizacion = (
        db.query(
            Cotizacion.solicitud_id.label("solicitud_id"),
            func.count(Cotizacion.id).label("proveedores_invitados"),
            func.sum(
                case((Cotizacion.estado == "respondida", 1), else_=0)
            ).label("respuestas_recibidas"),
        )
        .filter(Cotizacion.estado != "descartada")
        .group_by(Cotizacion.solicitud_id)
        .subquery()
    )

    recientes = (
        db.query(
            SolicitudCompra,
            func.coalesce(conteos_cotizacion.c.proveedores_invitados, 0),
            func.coalesce(conteos_cotizacion.c.respuestas_recibidas, 0),
        )
        .outerjoin(
            conteos_cotizacion,
            conteos_cotizacion.c.solicitud_id == SolicitudCompra.id,
        )
        .order_by(SolicitudCompra.created_at.desc())
        .limit(5)
        .all()
    )

    total_cotizaciones_vigentes = cotizaciones_pendientes + cotizaciones_respondidas
    tasa_respuesta = (
        round(cotizaciones_respondidas * 100 / total_cotizaciones_vigentes, 1)
        if total_cotizaciones_vigentes
        else 0
    )

    return DashboardResumenOut(
        oportunidades_activas=oportunidades_activas,
        cotizaciones_pendientes=cotizaciones_pendientes,
        cotizaciones_respondidas=cotizaciones_respondidas,
        proveedores_activos=proveedores_activos,
        tasa_respuesta=tasa_respuesta,
        oportunidades_por_estado=estados,
        oportunidades_recientes=[
            OportunidadRecienteOut(
                id=solicitud.id,
                numero=solicitud.numero,
                titulo=solicitud.titulo,
                estado=solicitud.estado,
                prioridad=solicitud.prioridad,
                fecha_requerida=solicitud.fecha_requerida,
                created_at=solicitud.created_at,
                proveedores_invitados=proveedores_invitados,
                respuestas_recibidas=respuestas_recibidas,
            )
            for solicitud, proveedores_invitados, respuestas_recibidas in recientes
        ],
    )
