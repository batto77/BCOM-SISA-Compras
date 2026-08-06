from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cotizaciones import Cotizacion, ItemCotizacion
from app.models.parametros import RubroPresupuestal
from app.models.solicitudes import SolicitudCompra, ItemSolicitud
from app.schemas.solicitudes import (
    SolicitudCompraCreate,
    SolicitudCompraUpdate,
)
from app.services.dav_generator import generar_proximo_dav


class CRUDSolicitud(CRUDBase[SolicitudCompra, SolicitudCompraCreate, SolicitudCompraUpdate]):

    def remove(self, db: Session, *, id: int) -> Optional[SolicitudCompra]:
        """Elimina primero las cotizaciones para respetar sus referencias a ítems."""
        db_obj = self.get(db, id)
        if not db_obj:
            return None

        try:
            cotizaciones = db.query(Cotizacion).filter(
                Cotizacion.solicitud_id == id
            ).all()
            for cotizacion in cotizaciones:
                db.delete(cotizacion)
            db.flush()

            db.delete(db_obj)
            db.commit()
            return db_obj
        except Exception:
            db.rollback()
            raise

    def create_with_items(
        self, db: Session, *, obj_in: SolicitudCompraCreate
    ) -> SolicitudCompra:
        items_data = obj_in.items
        data = obj_in.model_dump(exclude={"items", "rubro_ids"})
        rubro_ids = list(dict.fromkeys(obj_in.rubro_ids))
        if not rubro_ids and obj_in.rubro_id:
            rubro_ids = [obj_in.rubro_id]
        if rubro_ids:
            data["rubro_id"] = rubro_ids[0]

        # Generar automáticamente el número DAV (AAAA-NNNNN)
        data["numero"] = generar_proximo_dav(db)

        db_obj = SolicitudCompra(**data)
        db_obj.rubros = self._get_rubros(db, rubro_ids)

        db.add(db_obj)
        db.flush()  # obtener id sin commit aún

        for idx, item_in in enumerate(items_data):
            item_data = item_in.model_dump(exclude={"id"})
            # Asegurar orden secuencial si no se especificó
            if item_data.get("orden") == 0 and idx > 0:
                item_data["orden"] = idx
            db.add(ItemSolicitud(solicitud_id=db_obj.id, **item_data))

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_items(
        self,
        db: Session,
        *,
        db_obj: SolicitudCompra,
        obj_in: SolicitudCompraUpdate,
    ) -> SolicitudCompra:
        from fastapi import HTTPException, status as http_status
        if obj_in.numero is not None and obj_in.numero != db_obj.numero:
            exists = db.query(SolicitudCompra).filter(
                SolicitudCompra.numero == obj_in.numero,
                SolicitudCompra.id != db_obj.id,
            ).first()
            if exists:
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Ya existe una oportunidad con el número {obj_in.numero}",
                )
        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude={"items", "rubro_ids"},
        )
        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if "rubro_ids" in obj_in.model_fields_set:
            rubro_ids = list(dict.fromkeys(obj_in.rubro_ids or []))
            db_obj.rubros = self._get_rubros(db, rubro_ids)
            db_obj.rubro_id = rubro_ids[0] if rubro_ids else None
        elif "rubro_id" in obj_in.model_fields_set:
            db_obj.rubros = self._get_rubros(
                db,
                [obj_in.rubro_id] if obj_in.rubro_id else [],
            )

        if obj_in.items is not None:
            current_by_id = {item.id: item for item in db_obj.items}
            incoming_ids: set[int] = set()

            for idx, item_in in enumerate(obj_in.items):
                item_id = item_in.id
                item_data = item_in.model_dump(exclude={"id"})
                if item_data.get("orden") == 0 and idx > 0:
                    item_data["orden"] = idx
                if item_id and item_id in current_by_id:
                    incoming_ids.add(item_id)
                    item_obj = current_by_id[item_id]
                    for field, value in item_data.items():
                        setattr(item_obj, field, value)
                    db.add(item_obj)
                else:
                    db.add(ItemSolicitud(solicitud_id=db_obj.id, **item_data))

            for item in list(db_obj.items):
                if item.id in incoming_ids:
                    continue
                has_cotizaciones = db.query(ItemCotizacion).filter(
                    ItemCotizacion.item_solicitud_id == item.id
                ).first()
                if not has_cotizaciones:
                    db.delete(item)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        estado: Optional[str] = None,
    ) -> Tuple[List[SolicitudCompra], int]:
        query = db.query(self.model)
        if estado:
            query = query.filter(SolicitudCompra.estado == estado)
        query = query.order_by(SolicitudCompra.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def _get_rubros(
        self,
        db: Session,
        rubro_ids: List[int],
    ) -> List[RubroPresupuestal]:
        if not rubro_ids:
            return []
        rubros = (
            db.query(RubroPresupuestal)
            .filter(
                RubroPresupuestal.id.in_(rubro_ids),
                RubroPresupuestal.activo.is_(True),
            )
            .all()
        )
        rubros_by_id = {rubro.id: rubro for rubro in rubros}
        return [rubros_by_id[rubro_id] for rubro_id in rubro_ids if rubro_id in rubros_by_id]


crud_solicitud = CRUDSolicitud(SolicitudCompra)
