from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.catalogos import (
    crud_categoria_producto,
    crud_categoria_servicio,
    crud_definicion_campo,
    crud_producto,
    crud_servicio,
)
from app.models.catalogos import ModeloProducto
from app.database import get_db
from app.schemas.catalogos import (
    AsignarUnidadesRequest,
    CategoriaProductoClonarRequest,
    CategoriaProductoCreate,
    CategoriaProductoListOut,
    CategoriaProductoOut,
    CategoriaProductoUpdate,
    CategoriaServicioCreate,
    CategoriaServicioListOut,
    CategoriaServicioOut,
    CategoriaServicioUpdate,
    DefinicionCampoCreate,
    DefinicionCampoListOut,
    DefinicionCampoOut,
    DefinicionCampoUpdate,
    EspecificacionesBatchRequest,
    ModeloProductoCreate,
    ModeloProductoOut,
    ProductoCreate,
    ProductoListOut,
    ProductoOut,
    ProductoUpdate,
    ServicioCreate,
    ServicioListOut,
    ServicioOut,
    ServicioUpdate,
)

router = APIRouter()


# ─── Categorías de Producto ───────────────────────────────────────────────────

@router.get("/categorias-producto", response_model=CategoriaProductoListOut)
def listar_categorias_producto(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    items, total = crud_categoria_producto.get_multi(db, skip=skip, limit=limit)
    return CategoriaProductoListOut(items=items, total=total, skip=skip, limit=limit)


def _validar_nombre_categoria_libre(
    db: Session, nombre: str, exclude_id: Optional[int] = None
) -> None:
    """Rechaza nombres duplicados distinguiendo el caso de categorías desactivadas.

    Una categoría inactiva no aparece en el listado, así que un mensaje genérico
    de "ya existe" dejaría al usuario buscando algo que no puede ver.
    """
    existente = crud_categoria_producto.get_by_nombre(
        db, nombre=nombre, exclude_id=exclude_id
    )
    if not existente:
        return
    if existente.activo:
        raise HTTPException(
            status_code=409, detail="Ya existe una categoría con ese nombre."
        )
    raise HTTPException(
        status_code=409,
        detail=(
            f"Ya existe una categoría con ese nombre (#{existente.id}), "
            "pero está desactivada. Reactivala o elegí otro nombre."
        ),
    )


@router.post(
    "/categorias-producto",
    response_model=CategoriaProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria_producto(
    obj_in: CategoriaProductoCreate, db: Session = Depends(get_db)
):
    _validar_nombre_categoria_libre(db, obj_in.nombre)
    return crud_categoria_producto.create(db, obj_in=obj_in)


@router.get("/categorias-producto/{id}", response_model=CategoriaProductoOut)
def obtener_categoria_producto(id: int, db: Session = Depends(get_db)):
    obj = crud_categoria_producto.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    return obj


@router.put("/categorias-producto/{id}", response_model=CategoriaProductoOut)
def actualizar_categoria_producto(
    id: int, obj_in: CategoriaProductoUpdate, db: Session = Depends(get_db)
):
    obj = crud_categoria_producto.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    if obj_in.nombre:
        _validar_nombre_categoria_libre(db, obj_in.nombre, exclude_id=id)
    return crud_categoria_producto.update(db, db_obj=obj, obj_in=obj_in)


@router.post(
    "/categorias-producto/{id}/clonar",
    response_model=CategoriaProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def clonar_categoria_producto(
    id: int, obj_in: CategoriaProductoClonarRequest, db: Session = Depends(get_db)
):
    origen = crud_categoria_producto.get(db, id)
    if not origen:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    _validar_nombre_categoria_libre(db, obj_in.nombre)
    return crud_categoria_producto.clonar(db, origen=origen, nombre_nuevo=obj_in.nombre)


@router.delete("/categorias-producto/{id}", response_model=CategoriaProductoOut)
def eliminar_categoria_producto(id: int, db: Session = Depends(get_db)):
    obj = crud_categoria_producto.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    return obj


# ─── Campos de Categoría ──────────────────────────────────────────────────────

@router.get("/categorias-producto/{id}/campos", response_model=DefinicionCampoListOut)
def listar_campos_categoria(
    id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    cat = crud_categoria_producto.get(db, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    items, total = crud_definicion_campo.get_by_categoria(
        db, categoria_id=id, skip=skip, limit=limit
    )
    return DefinicionCampoListOut(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/categorias-producto/{id}/campos",
    response_model=DefinicionCampoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_campo(
    id: int, obj_in: DefinicionCampoCreate, db: Session = Depends(get_db)
):
    cat = crud_categoria_producto.get(db, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    return crud_definicion_campo.create_for_categoria(db, categoria_id=id, obj_in=obj_in)


@router.put("/campos/{id}", response_model=DefinicionCampoOut)
def editar_campo(id: int, obj_in: DefinicionCampoUpdate, db: Session = Depends(get_db)):
    obj = crud_definicion_campo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return crud_definicion_campo.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/campos/{id}", response_model=DefinicionCampoOut)
def desactivar_campo(id: int, db: Session = Depends(get_db)):
    obj = crud_definicion_campo.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return obj


@router.post("/campos/{id}/unidades", response_model=DefinicionCampoOut)
def asignar_unidades_campo(
    id: int, obj_in: AsignarUnidadesRequest, db: Session = Depends(get_db)
):
    obj = crud_definicion_campo.asignar_unidades(
        db, campo_id=id, unidad_ids=obj_in.unidad_ids
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return obj


@router.delete("/campos/{id}/unidades/{unidad_id}", response_model=DefinicionCampoOut)
def quitar_unidad_campo(id: int, unidad_id: int, db: Session = Depends(get_db)):
    obj = crud_definicion_campo.quitar_unidad(db, campo_id=id, unidad_id=unidad_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return obj


# ─── Productos ────────────────────────────────────────────────────────────────

@router.get("/productos", response_model=ProductoListOut)
def listar_productos(
    skip: int = 0,
    limit: int = 20,
    categoria_id: Optional[int] = None,
    etiqueta_ids: Optional[List[int]] = Query(default=None),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    items, total = crud_producto.get_multi_filtered(
        db,
        skip=skip,
        limit=limit,
        categoria_id=categoria_id,
        etiqueta_ids=etiqueta_ids,
        activo=activo,
    )
    return ProductoListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/productos", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(obj_in: ProductoCreate, db: Session = Depends(get_db)):
    if crud_producto.get_by_nombre(db, nombre=obj_in.nombre):
        raise HTTPException(
            status_code=409, detail="Ya existe un producto con ese nombre."
        )
    return crud_producto.create_with_relaciones(db, obj_in=obj_in)


@router.get("/productos/{id}", response_model=ProductoOut)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    obj = crud_producto.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj


@router.put("/productos/{id}", response_model=ProductoOut)
def actualizar_producto(
    id: int, obj_in: ProductoUpdate, db: Session = Depends(get_db)
):
    obj = crud_producto.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if obj_in.nombre and crud_producto.get_by_nombre(db, nombre=obj_in.nombre, exclude_id=id):
        raise HTTPException(
            status_code=409, detail="Ya existe un producto con ese nombre."
        )
    return crud_producto.update_with_relaciones(db, db_obj=obj, obj_in=obj_in)


@router.delete("/productos/{id}", response_model=ProductoOut)
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    obj = crud_producto.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj


@router.post("/productos/{id}/especificaciones", response_model=ProductoOut)
def upsert_especificaciones(
    id: int, obj_in: EspecificacionesBatchRequest, db: Session = Depends(get_db)
):
    producto = crud_producto.get(db, id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud_producto.upsert_especificaciones(
        db, producto_id=id, especificaciones=obj_in.especificaciones
    )


@router.post(
    "/productos/{id}/modelos",
    response_model=ModeloProductoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_modelo(
    id: int, obj_in: ModeloProductoCreate, db: Session = Depends(get_db)
):
    producto = crud_producto.get(db, id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud_producto.agregar_modelo(db, producto_id=id, obj_in=obj_in)


@router.delete("/modelos/{id}", response_model=ModeloProductoOut)
def eliminar_modelo(id: int, db: Session = Depends(get_db)):
    obj = db.query(ModeloProducto).filter(ModeloProducto.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    db.delete(obj)
    db.commit()
    return obj


# ─── Categorías de Servicio ───────────────────────────────────────────────────

@router.get("/categorias-servicio", response_model=CategoriaServicioListOut)
def listar_categorias_servicio(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    items, total = crud_categoria_servicio.get_multi(db, skip=skip, limit=limit)
    return CategoriaServicioListOut(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/categorias-servicio",
    response_model=CategoriaServicioOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria_servicio(
    obj_in: CategoriaServicioCreate, db: Session = Depends(get_db)
):
    return crud_categoria_servicio.create(db, obj_in=obj_in)


@router.get("/categorias-servicio/{id}", response_model=CategoriaServicioOut)
def obtener_categoria_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_categoria_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de servicio no encontrada")
    return obj


@router.put("/categorias-servicio/{id}", response_model=CategoriaServicioOut)
def actualizar_categoria_servicio(
    id: int, obj_in: CategoriaServicioUpdate, db: Session = Depends(get_db)
):
    obj = crud_categoria_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de servicio no encontrada")
    return crud_categoria_servicio.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/categorias-servicio/{id}", response_model=CategoriaServicioOut)
def eliminar_categoria_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_categoria_servicio.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría de servicio no encontrada")
    return obj


# ─── Servicios ────────────────────────────────────────────────────────────────

@router.get("/servicios", response_model=ServicioListOut)
def listar_servicios(
    skip: int = 0,
    limit: int = 20,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    items, total = crud_servicio.get_multi_filtered(
        db, skip=skip, limit=limit, activo=activo
    )
    return ServicioListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/servicios", response_model=ServicioOut, status_code=status.HTTP_201_CREATED)
def crear_servicio(obj_in: ServicioCreate, db: Session = Depends(get_db)):
    return crud_servicio.create_with_etiquetas(db, obj_in=obj_in)


@router.get("/servicios/{id}", response_model=ServicioOut)
def obtener_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return obj


@router.put("/servicios/{id}", response_model=ServicioOut)
def actualizar_servicio(
    id: int, obj_in: ServicioUpdate, db: Session = Depends(get_db)
):
    obj = crud_servicio.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return crud_servicio.update_with_etiquetas(db, db_obj=obj, obj_in=obj_in)


@router.delete("/servicios/{id}", response_model=ServicioOut)
def eliminar_servicio(id: int, db: Session = Depends(get_db)):
    obj = crud_servicio.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return obj


# ─── Estructura de campos por categoría (para frontend wizard) ────────────────

@router.get("/categorias/{categoria_id}/campos")
def get_campos_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Retorna la estructura de campos de una categoría."""
    from app.models.catalogos import CategoriaProducto, DefinicionCampo

    categoria = db.query(CategoriaProducto).filter(
        CategoriaProducto.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    campos = db.query(DefinicionCampo).filter(
        DefinicionCampo.categoria_producto_id == categoria_id,
        DefinicionCampo.activo == True
    ).order_by(DefinicionCampo.orden).all()

    return {
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "tipo": categoria.tipo,
        },
        "campos": [
            {
                "id": c.id,
                "nombre": c.nombre,
                "clave": c.clave,
                "tipo_dato": c.tipo_dato,
                "es_obligatorio": c.es_obligatorio,
                "tiene_cantidad": c.tiene_cantidad,
                "tiene_unidad": c.tiene_unidad,
                "unidad_default_id": c.unidad_default_id,
                "unidad_default": {
                    "id": c.unidad_default.id,
                    "nombre": c.unidad_default.nombre,
                    "simbolo": c.unidad_default.simbolo,
                } if c.unidad_default else None,
                "opciones_unidad": [
                    {"id": u.id, "nombre": u.nombre, "simbolo": u.simbolo}
                    for u in c.opciones_unidad
                ] if c.opciones_unidad else [],
                "placeholder": c.placeholder,
                "descripcion_ayuda": c.descripcion_ayuda,
            }
            for c in campos
        ]
    }
