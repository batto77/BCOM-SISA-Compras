from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.solicitudes import crud_solicitud
from app.database import get_db
from app.schemas.solicitudes import (
    SolicitudCompraCreate,
    SolicitudCompraOut,
    SolicitudCompraUpdate,
    SolicitudListOut,
)

router = APIRouter()


@router.get("/solicitudes", response_model=SolicitudListOut)
def listar_solicitudes(
    skip: int = 0,
    limit: int = 20,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
):
    items, total = crud_solicitud.get_multi_filtered(
        db, skip=skip, limit=limit, estado=estado
    )
    return SolicitudListOut(items=items, total=total, skip=skip, limit=limit)


def _log(db: Session, tabla: str, registro_id: int, accion: str, descripcion: str, datos: dict | None = None) -> None:
    from app.models.auditoria import AuditLog
    db.add(AuditLog(tabla=tabla, registro_id=registro_id, accion=accion, descripcion=descripcion, datos_nuevos=datos))
    db.commit()


@router.post(
    "/solicitudes",
    response_model=SolicitudCompraOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud(obj_in: SolicitudCompraCreate, db: Session = Depends(get_db)):
    obj = crud_solicitud.create_with_items(db, obj_in=obj_in)
    _log(db, "solicitudes_compra", obj.id, "create", f"Oportunidad creada: {obj.numero} — {obj.titulo}")
    return obj


@router.get("/solicitudes/{id}", response_model=SolicitudCompraOut)
def obtener_solicitud(id: int, db: Session = Depends(get_db)):
    obj = crud_solicitud.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    return obj


@router.put("/solicitudes/{id}", response_model=SolicitudCompraOut)
def actualizar_solicitud(
    id: int, obj_in: SolicitudCompraUpdate, db: Session = Depends(get_db)
):
    obj = crud_solicitud.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    result = crud_solicitud.update_with_items(db, db_obj=obj, obj_in=obj_in)
    _log(db, "solicitudes_compra", result.id, "update", f"Oportunidad actualizada: {result.numero} — {result.titulo}")
    return result


@router.delete("/solicitudes/{id}", response_model=SolicitudCompraOut)
def eliminar_solicitud(id: int, db: Session = Depends(get_db)):
    obj = crud_solicitud.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    _log(db, "solicitudes_compra", obj.id, "delete", f"Oportunidad eliminada: {obj.numero} — {obj.titulo}")
    return obj


@router.get("/solicitudes/{solicitud_id}/proveedores-sugeridos")
def get_proveedores_sugeridos(
    solicitud_id: int,
    db: Session = Depends(get_db),
):
    """
    Retorna todos los proveedores activos.
    Los que tienen etiquetas cuyo nombre coincide con los tipos de ítems
    de la oportunidad vienen marcados con `sugerido=True` y `score` mayor.
    """
    from app.models.solicitudes import ItemSolicitud
    from app.models.proveedores import Proveedor

    items = db.query(ItemSolicitud).filter(ItemSolicitud.solicitud_id == solicitud_id).all()
    proveedores = (
        db.query(Proveedor)
        .filter(Proveedor.estado == "activo")
        .all()
    )

    resultado = []
    for prov in proveedores:
        score = 0
        matched_item_ids: set[int] = set()
        prov_tag_ids = {e.id for e in (prov.etiquetas or [])}
        etiquetas_por_id = {e.id: e.nombre for e in (prov.etiquetas or [])}
        etiquetas_normalizadas = [
            (e.id, e.nombre, e.nombre.strip().lower())
            for e in (prov.etiquetas or [])
        ]
        criterios: list[dict] = []
        criterios_unicos: set[tuple[int, int, str]] = set()

        for item in items:
            item_matches = False
            item_specific_tag_ids: set[int] = set()
            if item.producto and item.producto.etiquetas:
                item_specific_tag_ids.update(etiqueta.id for etiqueta in item.producto.etiquetas)
            if item.servicio and item.servicio.etiquetas:
                item_specific_tag_ids.update(etiqueta.id for etiqueta in item.servicio.etiquetas)

            for etiqueta_id in item_specific_tag_ids.intersection(prov_tag_ids):
                item_matches = True
                score += 3
                criterio_key = (item.id, etiqueta_id, "etiqueta")
                if criterio_key not in criterios_unicos:
                    criterios_unicos.add(criterio_key)
                    criterios.append({
                        "tipo": "etiqueta",
                        "item_id": item.id,
                        "item_descripcion": item.descripcion,
                        "etiqueta": etiquetas_por_id[etiqueta_id],
                        "coincidencia": "Etiqueta configurada directamente en el ítem",
                    })

            item_tokens: dict[str, str] = {
                item.tipo.lower(): "Tipo de ítem",
            }
            if item.categoria_producto:
                item_tokens[item.categoria_producto.nombre.lower()] = "Categoría"
                item_tokens[item.categoria_producto.tipo.lower()] = "Tipo de categoría"
            if item.descripcion:
                for term in item.descripcion.split():
                    normalized_term = term.strip(".,;:()[]").lower()
                    if len(normalized_term) > 3:
                        item_tokens[normalized_term] = "Descripción"

            for token, origen in item_tokens.items():
                for etiqueta_id, etiqueta_nombre, etiqueta_normalizada in etiquetas_normalizadas:
                    if token not in etiqueta_normalizada and etiqueta_normalizada not in token:
                        continue
                    criterio_key = (item.id, etiqueta_id, origen)
                    if criterio_key in criterios_unicos:
                        continue
                    criterios_unicos.add(criterio_key)
                    criterios.append({
                        "tipo": origen.lower().replace(" ", "_"),
                        "item_id": item.id,
                        "item_descripcion": item.descripcion,
                        "etiqueta": etiqueta_nombre,
                        "coincidencia": f"{origen}: {token}",
                    })
                    item_matches = True
                    score += 1

            if item_matches:
                matched_item_ids.add(item.id)

        resultado.append({
            "id": prov.id,
            "razon_social": prov.razon_social,
            "nombre_comercial": prov.nombre_comercial,
            "pais": prov.pais,
            "estado": prov.estado,
            "sugerido": score > 0,
            "score": score,
            "item_ids_sugeridos": sorted(matched_item_ids),
            "criterios": criterios,
            "etiquetas": [{"id": e.id, "nombre": e.nombre} for e in (prov.etiquetas or [])],
        })

    # Ordenar: sugeridos primero, luego por nombre
    resultado.sort(key=lambda x: (-x["score"], x["razon_social"]))
    return resultado
