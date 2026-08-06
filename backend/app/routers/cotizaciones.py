from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.cotizaciones import crud_cotizacion
from app.database import get_db
from app.schemas.cotizaciones import (
    CotizacionCreate,
    CotizacionListOut,
    CotizacionOut,
    CotizacionUpdate,
    EnviarRFQRequest,
    ItemSolicitudMiniOut,
    ProveedorMiniOut,
    SolicitudMiniOut,
)

router = APIRouter()


def _log(db: Session, tabla: str, registro_id: int, accion: str, descripcion: str) -> None:
    from app.models.auditoria import AuditLog
    db.add(AuditLog(tabla=tabla, registro_id=registro_id, accion=accion, descripcion=descripcion))
    db.commit()


# ─── RFQ — ANTES de /{id} para evitar conflictos de routing ──────────────────

@router.post(
    "/cotizaciones/rfq",
    response_model=List[CotizacionOut],
    status_code=status.HTTP_201_CREATED,
    summary="Enviar RFQ a múltiples proveedores",
)
def enviar_rfq(obj_in: EnviarRFQRequest, db: Session = Depends(get_db)):
    """Crea cotizaciones para múltiples proveedores de una sola oportunidad."""
    creadas = crud_cotizacion.enviar_rfq(
        db,
        solicitud_id=obj_in.solicitud_id,
        proveedor_ids=obj_in.proveedor_ids,
        asignaciones=obj_in.asignaciones,
        fecha_limite=obj_in.fecha_limite_respuesta,
        notas=obj_in.notas_internas,
    )
    for c in creadas:
        _log(db, "cotizaciones", c.id, "create", f"RFQ enviado a proveedor #{c.proveedor_id} para solicitud #{c.solicitud_id}")
    return creadas


# ─── CRUD estándar de cotizaciones ───────────────────────────────────────────

@router.get("/cotizaciones", response_model=CotizacionListOut)
def listar_cotizaciones(
    skip: int = 0,
    limit: int = 20,
    solicitud_id: Optional[int] = None,
    estado: Optional[str] = None,
    proveedor_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    items, total = crud_cotizacion.get_multi_filtered(
        db,
        skip=skip,
        limit=limit,
        solicitud_id=solicitud_id,
        estado=estado,
        proveedor_id=proveedor_id,
    )
    return CotizacionListOut(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/cotizaciones",
    response_model=CotizacionOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_cotizacion(obj_in: CotizacionCreate, db: Session = Depends(get_db)):
    return crud_cotizacion.create_with_items(db, obj_in=obj_in)


@router.get("/cotizaciones/{id}", response_model=CotizacionOut)
def obtener_cotizacion(id: int, db: Session = Depends(get_db)):
    obj = crud_cotizacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return obj


@router.put("/cotizaciones/{id}", response_model=CotizacionOut)
def actualizar_cotizacion(
    id: int, obj_in: CotizacionUpdate, db: Session = Depends(get_db)
):
    obj = crud_cotizacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return crud_cotizacion.update_with_items(db, db_obj=obj, obj_in=obj_in)


@router.delete("/cotizaciones/{id}", response_model=CotizacionOut)
def eliminar_cotizacion(id: int, db: Session = Depends(get_db)):
    obj = crud_cotizacion.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return obj


# ─── Recordatorio al proveedor ───────────────────────────────────────────────

@router.post(
    "/cotizaciones/{id}/recordatorio",
    summary="Enviar recordatorio al proveedor",
)
def enviar_recordatorio(id: int, db: Session = Depends(get_db)):
    """
    Registra el intento de recordatorio. Cuando SMTP/SendGrid esté configurado,
    aquí se enviará el correo real. Por ahora devuelve los datos para que el
    usuario pueda hacerlo manualmente.
    """
    from datetime import datetime
    from app.models.cotizaciones import Cotizacion
    from app.models.proveedores import Proveedor

    cot = db.query(Cotizacion).filter(Cotizacion.id == id).first()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    if cot.estado == "respondida":
        raise HTTPException(status_code=409, detail="La cotización ya fue respondida")

    proveedor = db.query(Proveedor).filter(Proveedor.id == cot.proveedor_id).first()
    email_principal = None
    if proveedor:
        for contacto in (proveedor.contactos or []):
            for email_obj in (contacto.emails or []):
                if email_obj.es_principal or email_principal is None:
                    email_principal = email_obj.email

    link_cotizacion = f"/cotizar/{cot.token}" if cot.token else None

    return {
        "cotizacion_id": id,
        "proveedor": proveedor.razon_social if proveedor else None,
        "email": email_principal,
        "link": link_cotizacion,
        "fecha_recordatorio": datetime.utcnow().isoformat(),
        "simulado": True,
        "mensaje": (
            f"Recordatorio registrado. Correo destino: {email_principal or 'sin email configurado'}. "
            "La integración de envío SMTP se habilitará en la siguiente fase."
        ),
    }


# ─── Historial de versiones ──────────────────────────────────────────────────

@router.get(
    "/cotizaciones/{id}/versiones",
    summary="Historial de versiones de una cotización",
)
def historial_versiones(id: int, db: Session = Depends(get_db)):
    from app.models.cotizaciones import Cotizacion, CotizacionVersion
    import json

    cot = db.query(Cotizacion).filter(Cotizacion.id == id).first()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    versiones = (
        db.query(CotizacionVersion)
        .filter(CotizacionVersion.cotizacion_id == id)
        .order_by(CotizacionVersion.numero_version.desc())
        .all()
    )

    return {
        "cotizacion_id": id,
        "solicitud_titulo": cot.solicitud.titulo if cot.solicitud else None,
        "solicitud_numero": cot.solicitud.numero if cot.solicitud else None,
        "proveedor": cot.proveedor.razon_social if cot.proveedor else None,
        "version_actual": cot.version_actual,
        "estado": cot.estado,
        "versiones": [
            {
                "id": v.id,
                "numero_version": v.numero_version,
                "created_at": v.created_at.isoformat(),
                "snapshot": json.loads(v.snapshot_json) if v.snapshot_json else None,
            }
            for v in versiones
        ],
    }


# ─── Endpoints anidados bajo oportunidades ───────────────────────────────────

@router.get(
    "/solicitudes/{id}/cotizaciones",
    response_model=List[CotizacionOut],
    summary="Cotizaciones de una oportunidad",
)
def cotizaciones_por_solicitud(id: int, db: Session = Depends(get_db)):
    return crud_cotizacion.get_by_solicitud(db, solicitud_id=id)


@router.get(
    "/solicitudes/{id}/comparativo",
    summary="Comparativo de cotizaciones de una oportunidad",
)
def comparativo_solicitud(id: int, db: Session = Depends(get_db)):
    data = crud_cotizacion.get_comparativo(db, solicitud_id=id)

    solicitud = data["solicitud"]
    if not solicitud:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    # Serializar manualmente para devolver estructura limpia
    sol_schema = SolicitudMiniOut.model_validate(solicitud)

    items_sol = [
        ItemSolicitudMiniOut.model_validate(i) for i in data["items_solicitud"]
    ]

    cots_out = []
    for cot in data["cotizaciones"]:
        from app.schemas.cotizaciones import CotizacionOut as CotOut
        cots_out.append(CotOut.model_validate(cot).model_dump())

    # --- Evaluación ponderada (paso 3) ---
    from app.models.evaluacion import CriterioEvaluacion
    from app.services.evaluacion_scoring import resolver_pesos, calcular_evaluacion

    criterios_base = db.query(CriterioEvaluacion).order_by(CriterioEvaluacion.orden).all()
    pesos = resolver_pesos(solicitud.pesos_evaluacion, criterios_base)
    moneda_oportunidad = getattr(solicitud, "moneda", "COP") or "COP"
    evaluacion = calcular_evaluacion(
        db=db,
        items_solicitud=data["items_solicitud"],
        cotizaciones=data["cotizaciones"],
        pesos=pesos,
        moneda_oportunidad=moneda_oportunidad,
    )
    # Criterios (metadatos para la UI: nombre, orden)
    evaluacion["criterios"] = [
        {
            "clave": c.clave,
            "nombre": c.nombre,
            "descripcion": c.descripcion,
            "peso": float(pesos.get(c.clave, 0)),
            "orden": c.orden,
            "activo": c.activo,
        }
        for c in criterios_base
    ]

    return {
        "solicitud": sol_schema.model_dump(),
        "items_solicitud": [i.model_dump() for i in items_sol],
        "cotizaciones": cots_out,
        "evaluacion": evaluacion,
        # Selección/adjudicación confirmada por el usuario — se refleja en la UI.
        "cotizacion_ganadora_id": solicitud.cotizacion_ganadora_id,
        "justificacion_seleccion": solicitud.justificacion_seleccion,
        "adjudicacion_items": solicitud.adjudicacion_items or {},
    }


class AdjudicacionRequest(BaseModel):
    # {item_solicitud_id: cotizacion_id}. Un ítem con valor null/ausente queda sin adjudicar.
    adjudicacion: Dict[int, Optional[int]] = {}
    justificacion: Optional[str] = None


@router.post(
    "/solicitudes/{id}/adjudicar",
    summary="Guarda la adjudicación por ítem (la compra puede repartirse entre proveedores)",
)
def adjudicar_items(id: int, data: AdjudicacionRequest, db: Session = Depends(get_db)):
    from app.models.solicitudes import SolicitudCompra, ItemSolicitud
    from app.models.cotizaciones import Cotizacion

    solicitud = db.query(SolicitudCompra).filter(SolicitudCompra.id == id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    items_validos = {
        i.id for i in db.query(ItemSolicitud).filter(ItemSolicitud.solicitud_id == id).all()
    }
    cots_validas = {
        c.id for c in db.query(Cotizacion)
        .filter(Cotizacion.solicitud_id == id, Cotizacion.estado == "respondida").all()
    }

    limpia: Dict[str, int] = {}
    for item_id, cot_id in data.adjudicacion.items():
        item_id = int(item_id)
        if item_id not in items_validos:
            raise HTTPException(status_code=400, detail=f"Ítem {item_id} no pertenece a la oportunidad")
        if cot_id is None:
            continue  # ítem sin adjudicar
        if cot_id not in cots_validas:
            raise HTTPException(status_code=400, detail=f"La cotización {cot_id} no es una respuesta válida de esta oportunidad")
        limpia[str(item_id)] = cot_id

    solicitud.adjudicacion_items = limpia
    solicitud.justificacion_seleccion = data.justificacion
    # Si toda la adjudicación va a una sola cotización, la marcamos también como ganadora única.
    cots_elegidas = set(limpia.values())
    solicitud.cotizacion_ganadora_id = next(iter(cots_elegidas)) if len(cots_elegidas) == 1 else None

    _log(db, "solicitudes_compra", id, "update", f"Adjudicación por ítem actualizada ({len(limpia)} ítems)")
    db.commit()
    return {
        "adjudicacion_items": solicitud.adjudicacion_items,
        "cotizacion_ganadora_id": solicitud.cotizacion_ganadora_id,
        "justificacion_seleccion": solicitud.justificacion_seleccion,
    }


class SeleccionGanadorRequest(BaseModel):
    cotizacion_id: Optional[int] = None  # None = deshacer la selección
    justificacion: Optional[str] = None


@router.post(
    "/solicitudes/{id}/seleccionar-ganador",
    summary="Confirma (o deshace) la cotización ganadora de una oportunidad",
)
def seleccionar_ganador(id: int, data: SeleccionGanadorRequest, db: Session = Depends(get_db)):
    from app.models.solicitudes import SolicitudCompra
    from app.models.cotizaciones import Cotizacion

    solicitud = db.query(SolicitudCompra).filter(SolicitudCompra.id == id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")

    if data.cotizacion_id is not None:
        cot = (
            db.query(Cotizacion)
            .filter(Cotizacion.id == data.cotizacion_id, Cotizacion.solicitud_id == id)
            .first()
        )
        if not cot:
            raise HTTPException(status_code=400, detail="La cotización no pertenece a esta oportunidad")
        if cot.estado != "respondida":
            raise HTTPException(status_code=400, detail="Solo se puede seleccionar una cotización respondida")

    solicitud.cotizacion_ganadora_id = data.cotizacion_id
    solicitud.justificacion_seleccion = data.justificacion
    _log(
        db, "solicitudes_compra", id, "update",
        f"Ganador {'seleccionado: cotización #' + str(data.cotizacion_id) if data.cotizacion_id else 'deshecho'}",
    )
    db.commit()
    return {
        "cotizacion_ganadora_id": solicitud.cotizacion_ganadora_id,
        "justificacion_seleccion": solicitud.justificacion_seleccion,
    }
