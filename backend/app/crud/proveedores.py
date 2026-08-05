from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.etiquetas import Etiqueta
from app.models.proveedores import (
    Proveedor,
    ContactoProveedor,
    EmailContacto,
    TelefonoContacto,
)
from app.schemas.proveedores import (
    ProveedorCreate,
    ProveedorUpdate,
    ContactoProveedorCreate,
    ContactoProveedorUpdate,
    ContactoProveedorEmbedded,
    EmailContactoCreate,
    EmailContactoUpdate,
    TelefonoContactoCreate,
    TelefonoContactoUpdate,
)


class CRUDProveedor(CRUDBase[Proveedor, ProveedorCreate, ProveedorUpdate]):

    # ── helpers internos ─────────────────────────────────────────────────────

    def _sync_emails(
        self,
        db: Session,
        contacto: ContactoProveedor,
        emails_in: list,
    ) -> None:
        existing = {e.id: e for e in contacto.emails}
        incoming_ids = {e.id for e in emails_in if e.id is not None}
        # Eliminar los que ya no vienen
        for eid, e in list(existing.items()):
            if eid not in incoming_ids:
                db.delete(e)
        # Crear o actualizar
        for e_in in emails_in:
            if e_in.id is not None and e_in.id in existing:
                ee = existing[e_in.id]
                ee.email = str(e_in.email)
                ee.tipo = e_in.tipo
                ee.es_principal = e_in.es_principal
            else:
                db.add(EmailContacto(
                    contacto_id=contacto.id,
                    email=str(e_in.email),
                    tipo=e_in.tipo,
                    es_principal=e_in.es_principal,
                ))

    def _sync_telefonos(
        self,
        db: Session,
        contacto: ContactoProveedor,
        telefonos_in: list,
    ) -> None:
        existing = {t.id: t for t in contacto.telefonos}
        incoming_ids = {t.id for t in telefonos_in if t.id is not None}
        for tid, t in list(existing.items()):
            if tid not in incoming_ids:
                db.delete(t)
        for t_in in telefonos_in:
            if t_in.id is not None and t_in.id in existing:
                et = existing[t_in.id]
                et.numero = t_in.numero
                et.tipo = t_in.tipo
                et.extension = t_in.extension
            else:
                db.add(TelefonoContacto(
                    contacto_id=contacto.id,
                    numero=t_in.numero,
                    tipo=t_in.tipo,
                    extension=t_in.extension,
                ))

    def _create_contacto(
        self,
        db: Session,
        proveedor_id: int,
        c_in: "ContactoProveedorEmbedded",
    ) -> ContactoProveedor:
        new_c = ContactoProveedor(
            proveedor_id=proveedor_id,
            nombre=c_in.nombre,
            cargo=c_in.cargo,
            es_principal=c_in.es_principal,
            activo=c_in.activo,
        )
        db.add(new_c)
        db.flush()
        for e_in in c_in.emails:
            db.add(EmailContacto(
                contacto_id=new_c.id,
                email=str(e_in.email),
                tipo=e_in.tipo,
                es_principal=e_in.es_principal,
            ))
        for t_in in c_in.telefonos:
            db.add(TelefonoContacto(
                contacto_id=new_c.id,
                numero=t_in.numero,
                tipo=t_in.tipo,
                extension=t_in.extension,
            ))
        return new_c

    # ── CRUD público ─────────────────────────────────────────────────────────

    def create_with_etiquetas(
        self, db: Session, *, obj_in: ProveedorCreate
    ) -> Proveedor:
        data = obj_in.model_dump(exclude={"etiqueta_ids", "contactos"})
        # Auto-idioma
        if data.get("pais", "").lower() == "colombia":
            data["idioma"] = "ES"
        elif not data.get("idioma"):
            data["idioma"] = "EN"
        db_obj = Proveedor(**data)
        if obj_in.etiqueta_ids:
            etiquetas = (
                db.query(Etiqueta)
                .filter(Etiqueta.id.in_(obj_in.etiqueta_ids))
                .all()
            )
            db_obj.etiquetas = etiquetas
        db.add(db_obj)
        db.flush()  # obtener id sin hacer commit aún

        for c_in in obj_in.contactos:
            self._create_contacto(db, db_obj.id, c_in)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_etiquetas(
        self, db: Session, *, db_obj: Proveedor, obj_in: ProveedorUpdate
    ) -> Proveedor:
        update_data = obj_in.model_dump(
            exclude_unset=True, exclude={"etiqueta_ids", "contactos"}
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

        if obj_in.contactos is not None:
            existing = {c.id: c for c in db_obj.contactos}
            incoming_ids = {c.id for c in obj_in.contactos if c.id is not None}

            # Eliminar contactos que ya no vienen en el payload
            for cid, c in list(existing.items()):
                if cid not in incoming_ids:
                    db.delete(c)
            db.flush()

            for c_in in obj_in.contactos:
                if c_in.id is not None and c_in.id in existing:
                    # Actualizar contacto existente
                    ec = existing[c_in.id]
                    ec.nombre = c_in.nombre
                    ec.cargo = c_in.cargo
                    ec.es_principal = c_in.es_principal
                    ec.activo = c_in.activo
                    self._sync_emails(db, ec, c_in.emails)
                    self._sync_telefonos(db, ec, c_in.telefonos)
                else:
                    # Nuevo contacto
                    self._create_contacto(db, db_obj.id, c_in)

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
        pais: Optional[str] = None,
        etiqueta_ids: Optional[List[int]] = None,
    ) -> Tuple[List[Proveedor], int]:
        query = db.query(self.model)
        if estado:
            query = query.filter(Proveedor.estado == estado)
        if pais:
            query = query.filter(Proveedor.pais.ilike(f"%{pais}%"))
        if etiqueta_ids:
            query = query.filter(
                Proveedor.etiquetas.any(Etiqueta.id.in_(etiqueta_ids))
            )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def soft_delete(self, db: Session, *, id: int) -> Optional[Proveedor]:
        obj = self.get(db, id)
        if obj:
            obj.estado = "inactivo"
            obj.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(obj)
        return obj


class CRUDContactoProveedor(
    CRUDBase[ContactoProveedor, ContactoProveedorCreate, ContactoProveedorUpdate]
):
    def create_for_proveedor(
        self, db: Session, *, proveedor_id: int, obj_in: ContactoProveedorCreate
    ) -> ContactoProveedor:
        data = obj_in.model_dump()
        data["proveedor_id"] = proveedor_id
        db_obj = ContactoProveedor(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDEmailContacto(
    CRUDBase[EmailContacto, EmailContactoCreate, EmailContactoUpdate]
):
    def create_for_contacto(
        self, db: Session, *, contacto_id: int, obj_in: EmailContactoCreate
    ) -> EmailContacto:
        data = obj_in.model_dump()
        data["contacto_id"] = contacto_id
        db_obj = EmailContacto(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDTelefonoContacto(
    CRUDBase[TelefonoContacto, TelefonoContactoCreate, TelefonoContactoUpdate]
):
    def create_for_contacto(
        self, db: Session, *, contacto_id: int, obj_in: TelefonoContactoCreate
    ) -> TelefonoContacto:
        data = obj_in.model_dump()
        data["contacto_id"] = contacto_id
        db_obj = TelefonoContacto(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_proveedor = CRUDProveedor(Proveedor)
crud_contacto = CRUDContactoProveedor(ContactoProveedor)
crud_email = CRUDEmailContacto(EmailContacto)
crud_telefono = CRUDTelefonoContacto(TelefonoContacto)
