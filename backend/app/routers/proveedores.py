from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.proveedores import (
    crud_contacto,
    crud_email,
    crud_proveedor,
    crud_telefono,
)
from app.database import get_db
from app.schemas.proveedores import (
    ContactoProveedorCreate,
    ContactoProveedorOut,
    ContactoProveedorUpdate,
    EmailContactoCreate,
    EmailContactoOut,
    EmailContactoUpdate,
    ProveedorCreate,
    ProveedorListOut,
    ProveedorOut,
    ProveedorUpdate,
    TelefonoContactoCreate,
    TelefonoContactoOut,
    TelefonoContactoUpdate,
)
from app.services.proveedores_import import (
    construir_proveedor_desde_fila,
    generar_plantilla,
    parsear_archivo,
)

router = APIRouter()


def _log(db: Session, registro_id: int, accion: str, descripcion: str) -> None:
    from app.models.auditoria import AuditLog
    db.add(AuditLog(tabla="proveedores", registro_id=registro_id, accion=accion, descripcion=descripcion))
    db.commit()


# ─── Proveedores ─────────────────────────────────────────────────────────────

@router.get("/proveedores", response_model=ProveedorListOut)
def listar_proveedores(
    skip: int = 0,
    limit: int = 20,
    estado: Optional[str] = None,
    pais: Optional[str] = None,
    etiqueta_ids: Optional[List[int]] = Query(default=None),
    db: Session = Depends(get_db),
):
    items, total = crud_proveedor.get_multi_filtered(
        db, skip=skip, limit=limit, estado=estado, pais=pais, etiqueta_ids=etiqueta_ids
    )
    return ProveedorListOut(items=items, total=total, skip=skip, limit=limit)


@router.post("/proveedores", response_model=ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear_proveedor(obj_in: ProveedorCreate, db: Session = Depends(get_db)):
    result = crud_proveedor.create_with_etiquetas(db, obj_in=obj_in)
    _log(db, result.id, "create", f"Proveedor creado: {result.razon_social}")
    return result


@router.get("/proveedores/plantilla")
def descargar_plantilla_proveedores():
    contenido = generar_plantilla()
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_proveedores.xlsx"},
    )


@router.post("/proveedores/importar")
def importar_proveedores(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="El archivo debe ser .csv o .xlsx")

    contenido = file.file.read()
    try:
        filas = parsear_archivo(contenido, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    creados = 0
    omitidos_duplicados: List[str] = []
    errores: List[dict] = []

    for idx, fila in enumerate(filas, start=2):  # fila 1 = encabezados
        if not any((v or "").strip() if isinstance(v, str) else v for v in fila.values()):
            continue
        try:
            proveedor_in = construir_proveedor_desde_fila(fila)
        except (ValueError, ValidationError) as e:
            errores.append({"fila": idx, "motivo": str(e)})
            continue

        if proveedor_in.nit and crud_proveedor.get_by_nit(db, nit=proveedor_in.nit):
            omitidos_duplicados.append(proveedor_in.nit)
            continue

        try:
            result = crud_proveedor.create_with_etiquetas(db, obj_in=proveedor_in)
        except Exception as e:
            db.rollback()
            errores.append({"fila": idx, "motivo": f"Error al guardar: {e}"})
            continue

        creados += 1
        _log(db, result.id, "create", f"Proveedor creado por importación: {result.razon_social}")

    return {
        "creados": creados,
        "omitidos_duplicados": omitidos_duplicados,
        "errores": errores,
    }


@router.get("/proveedores/{id}", response_model=ProveedorOut)
def obtener_proveedor(id: int, db: Session = Depends(get_db)):
    obj = crud_proveedor.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return obj


@router.put("/proveedores/{id}", response_model=ProveedorOut)
def actualizar_proveedor(id: int, obj_in: ProveedorUpdate, db: Session = Depends(get_db)):
    obj = crud_proveedor.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    result = crud_proveedor.update_with_etiquetas(db, db_obj=obj, obj_in=obj_in)
    _log(db, result.id, "update", f"Proveedor actualizado: {result.razon_social}")
    return result


@router.delete("/proveedores/{id}", response_model=ProveedorOut)
def eliminar_proveedor(id: int, db: Session = Depends(get_db)):
    obj = crud_proveedor.soft_delete(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    _log(db, obj.id, "delete", f"Proveedor desactivado: {obj.razon_social}")
    return obj


# ─── Contactos ────────────────────────────────────────────────────────────────

@router.post(
    "/proveedores/{proveedor_id}/contactos",
    response_model=ContactoProveedorOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_contacto(
    proveedor_id: int,
    obj_in: ContactoProveedorCreate,
    db: Session = Depends(get_db),
):
    proveedor = crud_proveedor.get(db, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return crud_contacto.create_for_proveedor(db, proveedor_id=proveedor_id, obj_in=obj_in)


@router.put("/contactos/{id}", response_model=ContactoProveedorOut)
def editar_contacto(id: int, obj_in: ContactoProveedorUpdate, db: Session = Depends(get_db)):
    obj = crud_contacto.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return crud_contacto.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/contactos/{id}", response_model=ContactoProveedorOut)
def eliminar_contacto(id: int, db: Session = Depends(get_db)):
    obj = crud_contacto.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return obj


# ─── Emails ──────────────────────────────────────────────────────────────────

@router.post(
    "/contactos/{contacto_id}/emails",
    response_model=EmailContactoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_email(
    contacto_id: int,
    obj_in: EmailContactoCreate,
    db: Session = Depends(get_db),
):
    contacto = crud_contacto.get(db, contacto_id)
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return crud_email.create_for_contacto(db, contacto_id=contacto_id, obj_in=obj_in)


@router.put("/emails/{id}", response_model=EmailContactoOut)
def editar_email(id: int, obj_in: EmailContactoUpdate, db: Session = Depends(get_db)):
    obj = crud_email.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Email no encontrado")
    return crud_email.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/emails/{id}", response_model=EmailContactoOut)
def eliminar_email(id: int, db: Session = Depends(get_db)):
    obj = crud_email.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Email no encontrado")
    return obj


# ─── Teléfonos ───────────────────────────────────────────────────────────────

@router.post(
    "/contactos/{contacto_id}/telefonos",
    response_model=TelefonoContactoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_telefono(
    contacto_id: int,
    obj_in: TelefonoContactoCreate,
    db: Session = Depends(get_db),
):
    contacto = crud_contacto.get(db, contacto_id)
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return crud_telefono.create_for_contacto(db, contacto_id=contacto_id, obj_in=obj_in)


@router.put("/telefonos/{id}", response_model=TelefonoContactoOut)
def editar_telefono(id: int, obj_in: TelefonoContactoUpdate, db: Session = Depends(get_db)):
    obj = crud_telefono.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Teléfono no encontrado")
    return crud_telefono.update(db, db_obj=obj, obj_in=obj_in)


@router.delete("/telefonos/{id}", response_model=TelefonoContactoOut)
def eliminar_telefono(id: int, db: Session = Depends(get_db)):
    obj = crud_telefono.remove(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Teléfono no encontrado")
    return obj
