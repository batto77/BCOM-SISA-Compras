from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.parametros import (
    UnidadMedida,
    RubroPresupuestal,
    NivelAprobacion,
    PlantillaANS,
    TipoServicio,
)
from app.schemas.parametros import (
    UnidadMedidaCreate, UnidadMedidaUpdate,
    RubroPresupuestalCreate, RubroPresupuestalUpdate,
    NivelAprobacionCreate, NivelAprobacionUpdate,
    PlantillaANSCreate, PlantillaANSUpdate,
    TipoServicioCreate, TipoServicioUpdate,
)


class CRUDUnidadMedida(CRUDBase[UnidadMedida, UnidadMedidaCreate, UnidadMedidaUpdate]):
    def soft_delete(self, db: Session, *, id: int) -> Optional[UnidadMedida]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


class CRUDRubroPresupuestal(CRUDBase[RubroPresupuestal, RubroPresupuestalCreate, RubroPresupuestalUpdate]):
    def soft_delete(self, db: Session, *, id: int) -> Optional[RubroPresupuestal]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


class CRUDNivelAprobacion(CRUDBase[NivelAprobacion, NivelAprobacionCreate, NivelAprobacionUpdate]):
    pass


class CRUDPlantillaANS(CRUDBase[PlantillaANS, PlantillaANSCreate, PlantillaANSUpdate]):
    pass


class CRUDTipoServicio(CRUDBase[TipoServicio, TipoServicioCreate, TipoServicioUpdate]):
    def soft_delete(self, db: Session, *, id: int) -> Optional[TipoServicio]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


crud_unidad_medida = CRUDUnidadMedida(UnidadMedida)
crud_rubro_presupuestal = CRUDRubroPresupuestal(RubroPresupuestal)
crud_nivel_aprobacion = CRUDNivelAprobacion(NivelAprobacion)
crud_plantilla_ans = CRUDPlantillaANS(PlantillaANS)
crud_tipo_servicio = CRUDTipoServicio(TipoServicio)
