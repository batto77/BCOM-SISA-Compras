# Importar todos los modelos para que Alembic los detecte
from app.models.base import Base
from app.models.etiquetas import Dimension, Etiqueta
from app.models.parametros import (
    UnidadMedida,
    RubroPresupuestal,
    NivelAprobacion,
    PlantillaANS,
    TipoServicio,
)
from app.models.proveedores import (
    Proveedor,
    ContactoProveedor,
    EmailContacto,
    TelefonoContacto,
    proveedor_etiquetas,
)
from app.models.catalogos import (
    CategoriaProducto,
    DefinicionCampo,
    Producto,
    ValorEspecificacion,
    ModeloProducto,
    CategoriaServicio,
    Servicio,
    campo_unidades,
    producto_etiquetas,
    servicio_etiquetas,
)
from app.models.solicitudes import SolicitudCompra, ItemSolicitud, solicitud_rubros, CampoSolicitud
from app.models.cotizaciones import Cotizacion, CotizacionVersion, ItemCotizacion
from app.models.auditoria import AuditLog
from app.models.trm import TasaCambio, HistorialTasaCambio
from app.models.evaluacion import CriterioEvaluacion

__all__ = [
    "Base",
    "Dimension",
    "Etiqueta",
    "UnidadMedida",
    "RubroPresupuestal",
    "NivelAprobacion",
    "PlantillaANS",
    "TipoServicio",
    "Proveedor",
    "ContactoProveedor",
    "EmailContacto",
    "TelefonoContacto",
    "proveedor_etiquetas",
    "CategoriaProducto",
    "DefinicionCampo",
    "Producto",
    "ValorEspecificacion",
    "ModeloProducto",
    "CategoriaServicio",
    "Servicio",
    "campo_unidades",
    "producto_etiquetas",
    "servicio_etiquetas",
    "SolicitudCompra",
    "ItemSolicitud",
    "solicitud_rubros",
    "CampoSolicitud",
    "Cotizacion",
    "CotizacionVersion",
    "ItemCotizacion",
    "AuditLog",
    "TasaCambio",
    "HistorialTasaCambio",
    "CriterioEvaluacion",
]
