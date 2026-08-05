from app.crud.etiquetas import crud_dimension, crud_etiqueta
from app.crud.parametros import (
    crud_unidad_medida,
    crud_rubro_presupuestal,
    crud_nivel_aprobacion,
    crud_plantilla_ans,
    crud_tipo_servicio,
)
from app.crud.proveedores import (
    crud_proveedor,
    crud_contacto,
    crud_email,
    crud_telefono,
)
from app.crud.catalogos import (
    crud_categoria_producto,
    crud_definicion_campo,
    crud_producto,
    crud_categoria_servicio,
    crud_servicio,
)

__all__ = [
    "crud_dimension",
    "crud_etiqueta",
    "crud_unidad_medida",
    "crud_rubro_presupuestal",
    "crud_nivel_aprobacion",
    "crud_plantilla_ans",
    "crud_tipo_servicio",
    "crud_proveedor",
    "crud_contacto",
    "crud_email",
    "crud_telefono",
    "crud_categoria_producto",
    "crud_definicion_campo",
    "crud_producto",
    "crud_categoria_servicio",
    "crud_servicio",
]
