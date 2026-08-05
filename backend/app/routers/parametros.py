from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.parametros import (
    crud_unidad_medida,
    crud_rubro_presupuestal,
    crud_nivel_aprobacion,
    crud_plantilla_ans,
    crud_tipo_servicio,
)
from app.database import get_db
from app.schemas.parametros import (
    UnidadMedidaCreate, UnidadMedidaListOut, UnidadMedidaOut, UnidadMedidaUpdate,
    RubroPresupuestalCreate, RubroPresupuestalListOut, RubroPresupuestalOut, RubroPresupuestalUpdate,
    NivelAprobacionCreate, NivelAprobacionListOut, NivelAprobacionOut, NivelAprobacionUpdate,
    PlantillaANSCreate, PlantillaANSListOut, PlantillaANSOut, PlantillaANSUpdate,
    TipoServicioCreate, TipoServicioListOut, TipoServicioOut, TipoServicioUpdate,
)

router = APIRouter()


# ─── Unidades de Medida ───────────────────────────────────────────────────────

@router.get("/unidades-medida", response_model=UnidadMedidaListOut)
def listar_unidades_medida(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items, total = crud_unidad_medida.get_multi(db, skip=skip, limit=limit)
    return UnidadMedidaListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/unidades-medida", response_model=UnidadMedidaOut, status_code=status.HTTP_201_CREATED)
def crear_unidad_medida(obj_in: UnidadMedidaCreate, db: Session = Depends(get_db)):
    return crud_unidad_medida.create(db, obj_in=obj_in)


@router.get("/unidades-medida/{id}", response_model=UnidadMedidaOut)
def obtener_unidad_medida(id: int, db: Session = Depends(get_db)):
    obj = crud_unidad_medida.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return obj


@router.put("/unidades-medida/{id}", response_model=UnidadMedidaOut)
def actualizar_unidad_medida(id: int, obj_in: UnidadMedidaUpdate, db: Session = Depends(get_db)):
    obj = crud_unidad_medida.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return crud_unidad_medida.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/unidades-medida/{id}", response_model=UnidadMedidaOut)
def eliminar_unidad_medida(id: int, db: Session = Depends(get_db)):
    obj = crud_unidad_medida.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return obj


# ─── Rubros Presupuestales ────────────────────────────────────────────────────

@router.get("/rubros-presupuestales", response_model=RubroPresupuestalListOut)
def listar_rubros(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items, total = crud_rubro_presupuestal.get_multi(db, skip=skip, limit=limit)
    return RubroPresupuestalListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/rubros-presupuestales", response_model=RubroPresupuestalOut, status_code=status.HTTP_201_CREATED)
def crear_rubro(obj_in: RubroPresupuestalCreate, db: Session = Depends(get_db)):
    return crud_rubro_presupuestal.create(db, obj_in=obj_in)


@router.get("/rubros-presupuestales/{id}", response_model=RubroPresupuestalOut)
def obtener_rubro(id: int, db: Session = Depends(get_db)):
    obj = crud_rubro_presupuestal.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Rubro presupuestal no encontrado")
    return obj


@router.put("/rubros-presupuestales/{id}", response_model=RubroPresupuestalOut)
def actualizar_rubro(id: int, obj_in: RubroPresupuestalUpdate, db: Session = Depends(get_db)):
    obj = crud_rubro_presupuestal.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Rubro presupuestal no encontrado")
    return crud_rubro_presupuestal.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/rubros-presupuestales/{id}", response_model=RubroPresupuestalOut)
def eliminar_rubro(id: int, db: Session = Depends(get_db)):
    obj = crud_rubro_presupuestal.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Rubro presupuestal no encontrado")
    return obj


# ─── Niveles de Aprobación ────────────────────────────────────────────────────

@router.get("/niveles-aprobacion", response_model=NivelAprobacionListOut)
def listar_niveles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items, total = crud_nivel_aprobacion.get_multi(db, skip=skip, limit=limit)
    return NivelAprobacionListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/niveles-aprobacion", response_model=NivelAprobacionOut, status_code=status.HTTP_201_CREATED)
def crear_nivel(obj_in: NivelAprobacionCreate, db: Session = Depends(get_db)):
    return crud_nivel_aprobacion.create(db, obj_in=obj_in)


@router.get("/niveles-aprobacion/{id}", response_model=NivelAprobacionOut)
def obtener_nivel(id: int, db: Session = Depends(get_db)):
    obj = crud_nivel_aprobacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Nivel de aprobación no encontrado")
    return obj


@router.put("/niveles-aprobacion/{id}", response_model=NivelAprobacionOut)
def actualizar_nivel(id: int, obj_in: NivelAprobacionUpdate, db: Session = Depends(get_db)):
    obj = crud_nivel_aprobacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Nivel de aprobación no encontrado")
    return crud_nivel_aprobacion.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/niveles-aprobacion/{id}", response_model=NivelAprobacionOut)
def eliminar_nivel(id: int, db: Session = Depends(get_db)):
    obj = crud_nivel_aprobacion.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Nivel de aprobación no encontrado")
    return obj


# ─── Plantillas ANS ──────────────────────────────────────────────────────────

@router.get("/plantillas-ans", response_model=PlantillaANSListOut)
def listar_plantillas_ans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items, total = crud_plantilla_ans.get_multi(db, skip=skip, limit=limit)
    return PlantillaANSListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/plantillas-ans", response_model=PlantillaANSOut, status_code=status.HTTP_201_CREATED)
def crear_plantilla_ans(obj_in: PlantillaANSCreate, db: Session = Depends(get_db)):
    return crud_plantilla_ans.create(db, obj_in=obj_in)


@router.get("/plantillas-ans/{id}", response_model=PlantillaANSOut)
def obtener_plantilla_ans(id: int, db: Session = Depends(get_db)):
    obj = crud_plantilla_ans.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla ANS no encontrada")
    return obj


@router.put("/plantillas-ans/{id}", response_model=PlantillaANSOut)
def actualizar_plantilla_ans(id: int, obj_in: PlantillaANSUpdate, db: Session = Depends(get_db)):
    obj = crud_plantilla_ans.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla ANS no encontrada")
    return crud_plantilla_ans.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/plantillas-ans/{id}", response_model=PlantillaANSOut)
def eliminar_plantilla_ans(id: int, db: Session = Depends(get_db)):
    obj = crud_plantilla_ans.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla ANS no encontrada")
    return obj


# ─── Tipos de Servicio ────────────────────────────────────────────────────────

@router.get("/tipos-servicio", response_model=TipoServicioListOut)
def listar_tipos_servicio(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items, total = crud_tipo_servicio.get_multi(db, skip=skip, limit=limit)
    return TipoServicioListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/tipos-servicio", response_model=TipoServicioOut, status_code=status.HTTP_201_CREATED)
def crear_tipo_servicio(obj_in: TipoServicioCreate, db: Session = Depends(get_db)):
    return crud_tipo_servicio.create(db, obj_in=obj_in)


@router.get("/tipos-servicio/{id}", response_model=TipoServicioOut)
def obtener_tipo_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_tipo_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de servicio no encontrado")
    return obj


@router.put("/tipos-servicio/{id}", response_model=TipoServicioOut)
def actualizar_tipo_servicio(id: int, obj_in: TipoServicioUpdate, db: Session = Depends(get_db)):
    obj = crud_tipo_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de servicio no encontrado")
    return crud_tipo_servicio.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/tipos-servicio/{id}", response_model=TipoServicioOut)
def eliminar_tipo_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_tipo_servicio.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de servicio no encontrado")
    return obj
