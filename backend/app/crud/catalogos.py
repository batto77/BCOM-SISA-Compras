from datetime import datetime
import re
import unicodedata
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.catalogos import (
    CategoriaProducto,
    DefinicionCampo,
    Producto,
    ValorEspecificacion,
    ModeloProducto,
    CategoriaServicio,
    Servicio,
)
from app.models.etiquetas import Etiqueta
from app.models.parametros import UnidadMedida
from app.schemas.catalogos import (
    CategoriaProductoCreate, CategoriaProductoUpdate,
    DefinicionCampoCreate, DefinicionCampoUpdate,
    ProductoCreate, ProductoUpdate,
    ValorEspecificacionBase,
    ModeloProductoCreate,
    CategoriaServicioCreate, CategoriaServicioUpdate,
    ServicioCreate, ServicioUpdate,
)


class CRUDCategoriaProducto(
    CRUDBase[CategoriaProducto, CategoriaProductoCreate, CategoriaProductoUpdate]
):
    def create(
        self, db: Session, *, obj_in: CategoriaProductoCreate
    ) -> CategoriaProducto:
        data = obj_in.model_dump()
        requested_slug = data.get("slug") or data["nombre"]
        data["slug"] = self._unique_slug(db, requested_slug)
        db_obj = CategoriaProducto(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def _unique_slug(self, db: Session, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        base_slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
        base_slug = (base_slug or "categoria")[:100]
        candidate = base_slug
        suffix = 2

        while db.query(CategoriaProducto.id).filter(
            CategoriaProducto.slug == candidate
        ).first():
            suffix_text = f"-{suffix}"
            candidate = f"{base_slug[:100 - len(suffix_text)]}{suffix_text}"
            suffix += 1
        return candidate

    def soft_delete(self, db: Session, *, id: int) -> Optional[CategoriaProducto]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj

    def get_by_nombre(
        self, db: Session, *, nombre: str, exclude_id: Optional[int] = None
    ) -> Optional[CategoriaProducto]:
        query = db.query(CategoriaProducto).filter(
            func.lower(func.trim(CategoriaProducto.nombre)) == nombre.strip().lower(),
        )
        if exclude_id is not None:
            query = query.filter(CategoriaProducto.id != exclude_id)
        return query.first()

    def clonar(
        self, db: Session, *, origen: CategoriaProducto, nombre_nuevo: str
    ) -> CategoriaProducto:
        nueva = CategoriaProducto(
            nombre=nombre_nuevo,
            slug=self._unique_slug(db, nombre_nuevo),
            tipo=origen.tipo,
            icono=origen.icono,
            descripcion=origen.descripcion,
            activo=True,
        )
        db.add(nueva)
        db.flush()

        for campo in origen.campos:
            nuevo_campo = DefinicionCampo(
                categoria_producto_id=nueva.id,
                nombre=campo.nombre,
                clave=campo.clave,
                orden=campo.orden,
                tipo_dato=campo.tipo_dato,
                es_obligatorio=campo.es_obligatorio,
                es_campo_base=campo.es_campo_base,
                tiene_cantidad=campo.tiene_cantidad,
                tiene_unidad=campo.tiene_unidad,
                unidad_default_id=campo.unidad_default_id,
                placeholder=campo.placeholder,
                descripcion_ayuda=campo.descripcion_ayuda,
                activo=campo.activo,
            )
            nuevo_campo.opciones_unidad = list(campo.opciones_unidad)
            db.add(nuevo_campo)

        db.commit()
        db.refresh(nueva)
        return nueva


class CRUDDefinicionCampo(
    CRUDBase[DefinicionCampo, DefinicionCampoCreate, DefinicionCampoUpdate]
):
    def get_by_categoria(
        self, db: Session, categoria_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DefinicionCampo], int]:
        query = (
            db.query(DefinicionCampo)
            .filter(DefinicionCampo.categoria_producto_id == categoria_id)
            .order_by(DefinicionCampo.orden)
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create_for_categoria(
        self, db: Session, *, categoria_id: int, obj_in: DefinicionCampoCreate
    ) -> DefinicionCampo:
        data = obj_in.model_dump(exclude={"opciones_unidad_ids"})
        data["categoria_producto_id"] = categoria_id
        db_obj = DefinicionCampo(**data)
        if obj_in.opciones_unidad_ids:
            unidades = (
                db.query(UnidadMedida)
                .filter(UnidadMedida.id.in_(obj_in.opciones_unidad_ids))
                .all()
            )
            db_obj.opciones_unidad = unidades
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def asignar_unidades(
        self, db: Session, *, campo_id: int, unidad_ids: List[int]
    ) -> Optional[DefinicionCampo]:
        obj = self.get(db, campo_id)
        if not obj:
            return None
        unidades = (
            db.query(UnidadMedida).filter(UnidadMedida.id.in_(unidad_ids)).all()
        )
        obj.opciones_unidad = unidades
        db.commit()
        db.refresh(obj)
        return obj

    def quitar_unidad(
        self, db: Session, *, campo_id: int, unidad_id: int
    ) -> Optional[DefinicionCampo]:
        obj = self.get(db, campo_id)
        if not obj:
            return None
        obj.opciones_unidad = [u for u in obj.opciones_unidad if u.id != unidad_id]
        db.commit()
        db.refresh(obj)
        return obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[DefinicionCampo]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


class CRUDProducto(CRUDBase[Producto, ProductoCreate, ProductoUpdate]):
    def get_by_nombre(
        self, db: Session, *, nombre: str, exclude_id: Optional[int] = None
    ) -> Optional[Producto]:
        query = db.query(Producto).filter(
            Producto.activo.is_(True),
            func.lower(func.trim(Producto.nombre)) == nombre.strip().lower(),
        )
        if exclude_id is not None:
            query = query.filter(Producto.id != exclude_id)
        return query.first()

    def create_with_relaciones(
        self, db: Session, *, obj_in: ProductoCreate
    ) -> Producto:
        data = obj_in.model_dump(exclude={"etiqueta_ids", "especificaciones"})
        db_obj = Producto(**data)
        if obj_in.etiqueta_ids:
            etiquetas = (
                db.query(Etiqueta)
                .filter(Etiqueta.id.in_(obj_in.etiqueta_ids))
                .all()
            )
            db_obj.etiquetas = etiquetas
        db.add(db_obj)
        db.flush()
        # Crear especificaciones
        for esp_data in obj_in.especificaciones:
            esp = ValorEspecificacion(
                producto_id=db_obj.id,
                campo_id=esp_data.campo_id,
                cantidad=esp_data.cantidad,
                valor=esp_data.valor,
                unidad_medida_id=esp_data.unidad_medida_id,
            )
            db.add(esp)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_relaciones(
        self, db: Session, *, db_obj: Producto, obj_in: ProductoUpdate
    ) -> Producto:
        update_data = obj_in.model_dump(
            exclude_unset=True, exclude={"etiqueta_ids"}
        )
        update_data["updated_at"] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        if obj_in.etiqueta_ids is not None:
            etiquetas = (
                db.query(Etiqueta)
                .filter(Etiqueta.id.in_(obj_in.etiqueta_ids))
                .all()
            )
            db_obj.etiquetas = etiquetas
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
        categoria_id: Optional[int] = None,
        etiqueta_ids: Optional[List[int]] = None,
        activo: Optional[bool] = None,
    ) -> Tuple[List[Producto], int]:
        query = db.query(self.model)
        if categoria_id is not None:
            query = query.filter(Producto.categoria_producto_id == categoria_id)
        if etiqueta_ids:
            query = query.filter(
                Producto.etiquetas.any(Etiqueta.id.in_(etiqueta_ids))
            )
        if activo is not None:
            query = query.filter(Producto.activo == activo)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def upsert_especificaciones(
        self,
        db: Session,
        *,
        producto_id: int,
        especificaciones: List[ValorEspecificacionBase],
    ) -> Producto:
        for esp_data in especificaciones:
            existente = (
                db.query(ValorEspecificacion)
                .filter(
                    ValorEspecificacion.producto_id == producto_id,
                    ValorEspecificacion.campo_id == esp_data.campo_id,
                )
                .first()
            )
            if existente:
                existente.cantidad = esp_data.cantidad
                existente.valor = esp_data.valor
                existente.unidad_medida_id = esp_data.unidad_medida_id
            else:
                nueva = ValorEspecificacion(
                    producto_id=producto_id,
                    campo_id=esp_data.campo_id,
                    cantidad=esp_data.cantidad,
                    valor=esp_data.valor,
                    unidad_medida_id=esp_data.unidad_medida_id,
                )
                db.add(nueva)
        db.commit()
        return db.query(Producto).filter(Producto.id == producto_id).first()

    def agregar_modelo(
        self, db: Session, *, producto_id: int, obj_in: ModeloProductoCreate
    ) -> ModeloProducto:
        db_obj = ModeloProducto(producto_id=producto_id, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[Producto]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            obj.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(obj)
        return obj


class CRUDCategoriaServicio(
    CRUDBase[CategoriaServicio, CategoriaServicioCreate, CategoriaServicioUpdate]
):
    def soft_delete(self, db: Session, *, id: int) -> Optional[CategoriaServicio]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            db.commit()
            db.refresh(obj)
        return obj


class CRUDServicio(CRUDBase[Servicio, ServicioCreate, ServicioUpdate]):
    def create_with_etiquetas(
        self, db: Session, *, obj_in: ServicioCreate
    ) -> Servicio:
        data = obj_in.model_dump(exclude={"etiqueta_ids"})
        db_obj = Servicio(**data)
        if obj_in.etiqueta_ids:
            etiquetas = (
                db.query(Etiqueta)
                .filter(Etiqueta.id.in_(obj_in.etiqueta_ids))
                .all()
            )
            db_obj.etiquetas = etiquetas
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_etiquetas(
        self, db: Session, *, db_obj: Servicio, obj_in: ServicioUpdate
    ) -> Servicio:
        update_data = obj_in.model_dump(
            exclude_unset=True, exclude={"etiqueta_ids"}
        )
        update_data["updated_at"] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        if obj_in.etiqueta_ids is not None:
            etiquetas = (
                db.query(Etiqueta)
                .filter(Etiqueta.id.in_(obj_in.etiqueta_ids))
                .all()
            )
            db_obj.etiquetas = etiquetas
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
        activo: Optional[bool] = None,
    ) -> Tuple[List[Servicio], int]:
        query = db.query(self.model)
        if activo is not None:
            query = query.filter(Servicio.activo == activo)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def soft_delete(self, db: Session, *, id: int) -> Optional[Servicio]:
        obj = self.get(db, id)
        if obj:
            obj.activo = False
            obj.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(obj)
        return obj


crud_categoria_producto = CRUDCategoriaProducto(CategoriaProducto)
crud_definicion_campo = CRUDDefinicionCampo(DefinicionCampo)
crud_producto = CRUDProducto(Producto)
crud_categoria_servicio = CRUDCategoriaServicio(CategoriaServicio)
crud_servicio = CRUDServicio(Servicio)
