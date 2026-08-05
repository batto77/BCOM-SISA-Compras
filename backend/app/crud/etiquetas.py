from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.etiquetas import Dimension, Etiqueta
from app.schemas.etiquetas import (
    DimensionCreate, DimensionUpdate,
    EtiquetaCreate, EtiquetaUpdate,
)


class CRUDDimension(CRUDBase[Dimension, DimensionCreate, DimensionUpdate]):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Dimension], int]:
        query = db.query(self.model)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def soft_delete(self, db: Session, *, id: int) -> Optional[Dimension]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


class CRUDEtiqueta(CRUDBase[Etiqueta, EtiquetaCreate, EtiquetaUpdate]):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        dimension_id: Optional[int] = None,
        activo: Optional[bool] = None,
    ) -> Tuple[List[Etiqueta], int]:
        query = db.query(self.model)
        if dimension_id is not None:
            query = query.filter(Etiqueta.dimension_id == dimension_id)
        if activo is not None:
            query = query.filter(Etiqueta.activo == activo)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def soft_delete(self, db: Session, *, id: int) -> Optional[Etiqueta]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


crud_dimension = CRUDDimension(Dimension)
crud_etiqueta = CRUDEtiqueta(Etiqueta)
