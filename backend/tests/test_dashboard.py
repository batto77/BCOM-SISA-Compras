import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.cotizaciones import Cotizacion
from app.models.proveedores import Proveedor
from app.models.solicitudes import SolicitudCompra
from app.routers.dashboard import obtener_resumen_dashboard


class DashboardResumenTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(bind=engine)()

    def tearDown(self) -> None:
        self.db.close()

    def test_calcula_metricas_reales(self) -> None:
        solicitud = SolicitudCompra(
            numero="DAV-2026-001",
            titulo="Renovación",
            solicitante_nombre="Compras",
            fecha_requerida=date(2026, 6, 30),
            prioridad="alta",
            estado="en_cotizacion",
        )
        proveedor_activo = Proveedor(
            razon_social="Proveedor activo",
            pais="Colombia",
            estado="activo",
        )
        proveedor_inactivo = Proveedor(
            razon_social="Proveedor inactivo",
            pais="Colombia",
            estado="inactivo",
        )
        self.db.add_all([solicitud, proveedor_activo, proveedor_inactivo])
        self.db.flush()
        self.db.add_all([
            Cotizacion(
                solicitud_id=solicitud.id,
                proveedor_id=proveedor_activo.id,
                estado="invitada",
            ),
            Cotizacion(
                solicitud_id=solicitud.id,
                proveedor_id=proveedor_inactivo.id,
                estado="respondida",
            ),
        ])
        self.db.commit()

        resumen = obtener_resumen_dashboard(self.db)

        self.assertEqual(resumen.oportunidades_activas, 1)
        self.assertEqual(resumen.cotizaciones_pendientes, 1)
        self.assertEqual(resumen.cotizaciones_respondidas, 1)
        self.assertEqual(resumen.proveedores_activos, 1)
        self.assertEqual(resumen.tasa_respuesta, 50)
        self.assertEqual(resumen.oportunidades_recientes[0].proveedores_invitados, 2)
        self.assertEqual(resumen.oportunidades_recientes[0].respuestas_recibidas, 1)
