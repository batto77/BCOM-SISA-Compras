import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cotizaciones import Cotizacion, CotizacionVersion, ItemCotizacion
from app.models.solicitudes import SolicitudCompra, ItemSolicitud
from app.schemas.cotizaciones import (
    CotizacionCreate,
    CotizacionUpdate,
)


class CRUDCotizacion(CRUDBase[Cotizacion, CotizacionCreate, CotizacionUpdate]):

    @staticmethod
    def _json_default(value: Any) -> str:
        if isinstance(value, (datetime, Decimal)):
            return str(value)
        return str(value)

    def _build_snapshot(self, cotizacion: Cotizacion) -> str:
        solicitud = cotizacion.solicitud
        proveedor = cotizacion.proveedor
        payload = {
            "cotizacion_id": cotizacion.id,
            "solicitud_id": cotizacion.solicitud_id,
            "proveedor_id": cotizacion.proveedor_id,
            "proveedor": {
                "id": proveedor.id,
                "razon_social": proveedor.razon_social,
                "nombre_comercial": proveedor.nombre_comercial,
            } if proveedor else None,
            "version": cotizacion.version_actual,
            "estado": cotizacion.estado,
            "respuesta_version": cotizacion.respuesta_version,
            "fecha_limite_respuesta": cotizacion.fecha_limite_respuesta,
            "notas_internas": cotizacion.notas_internas,
            "notas_proveedor": cotizacion.notas_proveedor,
            "solicitud": {
                "id": solicitud.id,
                "numero": solicitud.numero,
                "titulo": solicitud.titulo,
                "version": solicitud.version_actual,
                "prioridad": solicitud.prioridad,
                "fecha_requerida": solicitud.fecha_requerida,
            } if solicitud else None,
            "items": [
                {
                    "item_cotizacion_id": item.id,
                    "item_solicitud_id": item.item_solicitud_id,
                    "orden": item.orden,
                    "precio_unitario": item.precio_unitario,
                    "tiempo_entrega_dias": item.tiempo_entrega_dias,
                    "disponible": item.disponible,
                    "notas": item.notas,
                    "solicitud_item": {
                        "id": item.item_solicitud.id,
                        "tipo": item.item_solicitud.tipo,
                        "descripcion": item.item_solicitud.descripcion,
                        "cantidad": item.item_solicitud.cantidad,
                        "unidad_medida_id": item.item_solicitud.unidad_medida_id,
                        "producto_id": item.item_solicitud.producto_id,
                        "categoria_producto_id": item.item_solicitud.categoria_producto_id,
                        "servicio_id": item.item_solicitud.servicio_id,
                        "especificaciones": item.item_solicitud.especificaciones,
                        "notas": item.item_solicitud.notas,
                    } if item.item_solicitud else None,
                }
                for item in cotizacion.items
            ],
        }
        return json.dumps(payload, default=self._json_default, ensure_ascii=False)

    def _ensure_version_snapshot(self, db: Session, *, cotizacion: Cotizacion) -> None:
        exists = db.query(CotizacionVersion).filter(
            CotizacionVersion.cotizacion_id == cotizacion.id,
            CotizacionVersion.numero_version == cotizacion.version_actual,
        ).first()
        if exists:
            exists.snapshot_json = self._build_snapshot(cotizacion)
            return
        db.add(CotizacionVersion(
            cotizacion_id=cotizacion.id,
            numero_version=cotizacion.version_actual,
            snapshot_json=self._build_snapshot(cotizacion),
        ))

    @staticmethod
    def _replace_items(
        db: Session,
        *,
        cotizacion: Cotizacion,
        items_solicitud: List[ItemSolicitud],
    ) -> None:
        for item in list(cotizacion.items):
            db.delete(item)
        db.flush()

        for idx, item_sol in enumerate(items_solicitud):
            db.add(ItemCotizacion(
                cotizacion_id=cotizacion.id,
                item_solicitud_id=item_sol.id,
                precio_unitario=None,
                disponible=True,
                orden=item_sol.orden if item_sol.orden > 0 else idx,
            ))

    def create_with_items(
        self, db: Session, *, obj_in: CotizacionCreate
    ) -> Cotizacion:
        items_data = obj_in.items
        data = obj_in.model_dump(exclude={"items"})
        db_obj = Cotizacion(**data)
        db.add(db_obj)
        db.flush()  # obtener id sin commit aún

        for idx, item_in in enumerate(items_data):
            item_data = item_in.model_dump()
            if item_data.get("orden") == 0 and idx > 0:
                item_data["orden"] = idx
            db.add(ItemCotizacion(cotizacion_id=db_obj.id, **item_data))

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_items(
        self,
        db: Session,
        *,
        db_obj: Cotizacion,
        obj_in: CotizacionUpdate,
    ) -> Cotizacion:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"items"})
        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if obj_in.items is not None:
            # Eliminar todos los items existentes
            for item in list(db_obj.items):
                db.delete(item)
            db.flush()

            # Crear los nuevos items
            for idx, item_in in enumerate(obj_in.items):
                item_data = item_in.model_dump()
                if item_data.get("orden") == 0 and idx > 0:
                    item_data["orden"] = idx
                db.add(ItemCotizacion(cotizacion_id=db_obj.id, **item_data))

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def enviar_rfq(
        self,
        db: Session,
        *,
        solicitud_id: int,
        proveedor_ids: List[int],
        asignaciones: Optional[Dict[int, List[int]]] = None,
        fecha_limite: Optional[object] = None,
        notas: Optional[str] = None,
    ) -> List[Cotizacion]:
        # Obtener la solicitud
        solicitud = (
            db.query(SolicitudCompra)
            .filter(SolicitudCompra.id == solicitud_id)
            .with_for_update(of=SolicitudCompra)
            .first()
        )
        if not solicitud:
            return []

        # Obtener items de la solicitud
        items_solicitud = db.query(ItemSolicitud).filter(
            ItemSolicitud.solicitud_id == solicitud_id
        ).order_by(ItemSolicitud.orden).all()
        items_by_id = {item.id: item for item in items_solicitud}
        asignaciones = asignaciones or {}

        tiene_rfq_publicado = db.query(Cotizacion.id).filter(
            Cotizacion.solicitud_id == solicitud_id,
            Cotizacion.estado != "descartada",
        ).first() is not None
        version_publicacion = (
            (solicitud.version_actual or 1) + 1
            if tiene_rfq_publicado
            else (solicitud.version_actual or 1)
        )

        creadas: List[Cotizacion] = []

        for proveedor_id in proveedor_ids:
            assigned_ids = asignaciones.get(proveedor_id) or asignaciones.get(str(proveedor_id))  # type: ignore[arg-type]
            if assigned_ids is None:
                assigned_items = items_solicitud
            else:
                assigned_items = [
                    items_by_id[item_id]
                    for item_id in assigned_ids
                    if item_id in items_by_id
                ]

            if not assigned_items:
                continue

            existente = db.query(Cotizacion).filter(
                Cotizacion.solicitud_id == solicitud_id,
                Cotizacion.proveedor_id == proveedor_id,
                Cotizacion.estado != "descartada",
            ).first()

            if existente:
                self._ensure_version_snapshot(db, cotizacion=existente)
                existente.version_actual = version_publicacion
                existente.estado = "invitada"
                existente.fecha_limite_respuesta = fecha_limite
                existente.notas_internas = notas
                existente.updated_at = datetime.utcnow()
                self._replace_items(db, cotizacion=existente, items_solicitud=assigned_items)
                db.flush()
                db.refresh(existente)
                self._ensure_version_snapshot(db, cotizacion=existente)
                creadas.append(existente)
                continue

            # Crear la cotización
            cot = Cotizacion(
                solicitud_id=solicitud_id,
                proveedor_id=proveedor_id,
                estado="invitada",
                version_actual=version_publicacion,
                fecha_limite_respuesta=fecha_limite,
                notas_internas=notas,
                token=str(uuid.uuid4()),
            )
            db.add(cot)
            db.flush()

            # Copiar items de la solicitud como items de cotización
            for idx, item_sol in enumerate(assigned_items):
                item_cot = ItemCotizacion(
                    cotizacion_id=cot.id,
                    item_solicitud_id=item_sol.id,
                    precio_unitario=None,
                    disponible=True,
                    orden=item_sol.orden if item_sol.orden > 0 else idx,
                )
                db.add(item_cot)

            db.flush()
            db.refresh(cot)
            self._ensure_version_snapshot(db, cotizacion=cot)
            creadas.append(cot)

        # Actualizar estado de la solicitud a 'en_cotizacion'
        if creadas:
            solicitud.estado = "en_cotizacion"
            solicitud.version_actual = version_publicacion
            solicitud.updated_at = datetime.utcnow()

        db.commit()

        # Refrescar objetos para cargar relaciones
        for cot in creadas:
            db.refresh(cot)

        return creadas

    def get_by_token(self, db: Session, *, token: str) -> Optional[Cotizacion]:
        return db.query(self.model).filter(Cotizacion.token == token).first()

    def get_by_solicitud(
        self, db: Session, *, solicitud_id: int
    ) -> List[Cotizacion]:
        return (
            db.query(self.model)
            .filter(Cotizacion.solicitud_id == solicitud_id)
            .order_by(Cotizacion.created_at.asc())
            .all()
        )

    def get_multi_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        solicitud_id: Optional[int] = None,
        estado: Optional[str] = None,
        proveedor_id: Optional[int] = None,
    ) -> Tuple[List[Cotizacion], int]:
        query = db.query(self.model)
        if solicitud_id is not None:
            query = query.filter(Cotizacion.solicitud_id == solicitud_id)
        if estado:
            query = query.filter(Cotizacion.estado == estado)
        if proveedor_id is not None:
            query = query.filter(Cotizacion.proveedor_id == proveedor_id)
        query = query.order_by(Cotizacion.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_comparativo(self, db: Session, *, solicitud_id: int) -> dict:
        solicitud = db.query(SolicitudCompra).filter(
            SolicitudCompra.id == solicitud_id
        ).first()

        items_solicitud = db.query(ItemSolicitud).filter(
            ItemSolicitud.solicitud_id == solicitud_id
        ).order_by(ItemSolicitud.orden).all()

        cotizaciones = (
            db.query(Cotizacion)
            .filter(Cotizacion.solicitud_id == solicitud_id)
            .order_by(Cotizacion.created_at.asc())
            .all()
        )

        return {
            "solicitud": solicitud,
            "items_solicitud": items_solicitud,
            "cotizaciones": cotizaciones,
        }


crud_cotizacion = CRUDCotizacion(Cotizacion)
