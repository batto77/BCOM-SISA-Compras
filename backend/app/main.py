import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

UPLOADS_DIR = "/app/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

from sqlalchemy import inspect, text

from app.database import engine, SessionLocal
from app.models import Base  # noqa: F401 — importa todos los modelos para create_all
from app.routers import (
    auditoria,
    campos_solicitud,
    catalogos,
    cotizaciones,
    dashboard,
    etiquetas,
    evaluacion,
    parametros,
    proveedores,
    public,
    solicitudes,
    trm,
)
from app.seed import seed_initial_data, seed_example_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Migraciones manuales defensivas para columnas nuevas en bases existentes.
    with engine.connect() as conn:
        inspector = inspect(conn)
        columns_by_table = {
            table_name: {column["name"] for column in inspector.get_columns(table_name)}
            for table_name in inspector.get_table_names()
        }
        if "numero" not in columns_by_table.get("solicitudes_compra", set()):
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN numero VARCHAR(20)"))
        if "aprobador" not in columns_by_table.get("solicitudes_compra", set()):
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN aprobador VARCHAR(200)"))
        if "version_actual" not in columns_by_table.get("solicitudes_compra", set()):
            conn.execute(text(
                "ALTER TABLE solicitudes_compra "
                "ADD COLUMN version_actual INTEGER NOT NULL DEFAULT 1"
            ))
            conn.execute(text(
                """
                UPDATE solicitudes_compra AS solicitud
                SET version_actual = COALESCE(
                    (
                        SELECT MAX(cotizacion.version_actual)
                        FROM cotizaciones AS cotizacion
                        WHERE cotizacion.solicitud_id = solicitud.id
                          AND cotizacion.estado != 'descartada'
                    ),
                    1
                )
                """
            ))
        if "solicitud_rubros" in inspector.get_table_names():
            conn.execute(text(
                """
                INSERT INTO solicitud_rubros (solicitud_id, rubro_id)
                SELECT id, rubro_id
                FROM solicitudes_compra
                WHERE rubro_id IS NOT NULL
                ON CONFLICT DO NOTHING
                """
            ))
        item_solicitud_columns = columns_by_table.get("items_solicitud", set())
        if "categoria_producto_id" not in item_solicitud_columns:
            conn.execute(text("ALTER TABLE items_solicitud ADD COLUMN categoria_producto_id INTEGER"))
        cotizacion_columns = columns_by_table.get("cotizaciones", set())
        if "token" not in cotizacion_columns:
            conn.execute(text("ALTER TABLE cotizaciones ADD COLUMN token VARCHAR(36)"))
        if "version_actual" not in cotizacion_columns:
            conn.execute(text("ALTER TABLE cotizaciones ADD COLUMN version_actual INTEGER NOT NULL DEFAULT 1"))
        if "respuesta_version" not in cotizacion_columns:
            conn.execute(text("ALTER TABLE cotizaciones ADD COLUMN respuesta_version INTEGER"))
        items_cotizacion_columns = columns_by_table.get("items_cotizacion", set())
        if "valores_especificacion" not in items_cotizacion_columns:
            conn.execute(text("ALTER TABLE items_cotizacion ADD COLUMN IF NOT EXISTS valores_especificacion JSONB DEFAULT NULL"))
        proveedor_columns = columns_by_table.get("proveedores", set())
        if "nit" not in proveedor_columns:
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN nit VARCHAR(30)"))
        if "tipo_persona" not in proveedor_columns:
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN tipo_persona VARCHAR(20)"))
        if "monedas" not in proveedor_columns:
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN monedas JSONB DEFAULT NULL"))
        if "moneda_defecto" not in proveedor_columns:
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN moneda_defecto VARCHAR(3) DEFAULT NULL"))
        if "calificacion" not in proveedor_columns:
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN IF NOT EXISTS calificacion NUMERIC(3,1) DEFAULT NULL"))
        # Tabla campos_solicitud (nueva)
        if "campos_solicitud" not in inspector.get_table_names():
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS campos_solicitud (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion VARCHAR(255),
                    tipo_dato VARCHAR(20) NOT NULL DEFAULT 'texto',
                    opciones JSONB,
                    obligatorio BOOLEAN NOT NULL DEFAULT FALSE,
                    activo BOOLEAN NOT NULL DEFAULT TRUE,
                    orden INTEGER NOT NULL DEFAULT 0
                )
            """))
        # Columna campos_extra en solicitudes_compra
        solicitud_cols = columns_by_table.get("solicitudes_compra", set())
        if "campos_extra" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN campos_extra JSONB DEFAULT NULL"))
        # Columnas de evaluación / selección de ganador en solicitudes_compra
        if "pesos_evaluacion" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS pesos_evaluacion JSONB DEFAULT NULL"))
        if "cotizacion_ganadora_id" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS cotizacion_ganadora_id INTEGER DEFAULT NULL"))
        if "justificacion_seleccion" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS justificacion_seleccion TEXT DEFAULT NULL"))
        if "adjudicacion_items" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS adjudicacion_items JSONB DEFAULT NULL"))
        if "moneda" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS moneda VARCHAR(3) DEFAULT 'COP'"))
        # Cancelación y adjudicación de la oportunidad
        if "motivo_cancelacion" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS motivo_cancelacion TEXT DEFAULT NULL"))
        if "fecha_cancelacion" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS fecha_cancelacion TIMESTAMP DEFAULT NULL"))
        if "fecha_adjudicacion" not in solicitud_cols:
            conn.execute(text("ALTER TABLE solicitudes_compra ADD COLUMN IF NOT EXISTS fecha_adjudicacion TIMESTAMP DEFAULT NULL"))
        # Prioridades por impacto en la operación: urgente/alta/normal/baja → critico/alto/medio/bajo
        conn.execute(text("""
            UPDATE solicitudes_compra SET prioridad = CASE prioridad
                WHEN 'urgente' THEN 'critico'
                WHEN 'alta'    THEN 'alto'
                WHEN 'normal'  THEN 'medio'
                WHEN 'baja'    THEN 'bajo'
                ELSE prioridad
            END
            WHERE prioridad IN ('urgente', 'alta', 'normal', 'baja')
        """))
        # Garantía ofrecida por el proveedor, en meses (0 = no aplica)
        if "garantia_meses" not in items_cotizacion_columns:
            conn.execute(text("ALTER TABLE items_cotizacion ADD COLUMN IF NOT EXISTS garantia_meses INTEGER DEFAULT 0"))
        # Tabla paramétrica de criterios de evaluación
        if "criterios_evaluacion" not in inspector.get_table_names():
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS criterios_evaluacion (
                    id SERIAL PRIMARY KEY,
                    clave VARCHAR(40) UNIQUE NOT NULL,
                    nombre VARCHAR(120) NOT NULL,
                    descripcion VARCHAR(255),
                    peso_default NUMERIC(5,2) NOT NULL DEFAULT 0,
                    orden INTEGER NOT NULL DEFAULT 0,
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                )
            """))
        # Columnas para PDFs adjuntos
        if "ficha_tecnica_path" not in items_cotizacion_columns:
            conn.execute(text("ALTER TABLE items_cotizacion ADD COLUMN IF NOT EXISTS ficha_tecnica_path VARCHAR(500)"))
        if "pdf_cotizacion_path" not in cotizacion_columns:
            conn.execute(text("ALTER TABLE cotizaciones ADD COLUMN IF NOT EXISTS pdf_cotizacion_path VARCHAR(500)"))
        # Columna moneda por ítem cotizado
        if "moneda" not in items_cotizacion_columns:
            conn.execute(text("ALTER TABLE items_cotizacion ADD COLUMN IF NOT EXISTS moneda VARCHAR(3)"))
        # Tabla historial de tasas de cambio
        if "historial_tasas_cambio" not in inspector.get_table_names():
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS historial_tasas_cambio (
                    id SERIAL PRIMARY KEY,
                    moneda VARCHAR(3) NOT NULL,
                    tasa_cop_anterior NUMERIC(15,4),
                    tasa_cop_nueva NUMERIC(15,4) NOT NULL,
                    usuario VARCHAR(200),
                    created_at TIMESTAMP NOT NULL DEFAULT now()
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_historial_tasas_moneda ON historial_tasas_cambio (moneda)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_historial_tasas_created ON historial_tasas_cambio (created_at)"))
        conn.commit()

    # Seed TRM inicial (USD y EUR a valores por defecto si no existen)
    from app.models.trm import TasaCambio
    from app.models.evaluacion import CriterioEvaluacion
    db_seed = SessionLocal()
    try:
        for moneda, tasa in [("USD", 4200), ("EUR", 4600), ("GBP", 5300)]:
            if not db_seed.query(TasaCambio).filter(TasaCambio.moneda == moneda).first():
                db_seed.add(TasaCambio(moneda=moneda, tasa_cop=tasa))
        # Criterios de evaluación base (pesos por defecto que suman 100)
        criterios_base = [
            ("financiero", "Financiero", "Precios propuestos en las cotizaciones", 40, 1),
            ("tiempo_entrega", "Tiempo de entrega", "Días de entrega propuestos por el proveedor", 30, 2),
            ("completitud", "Completitud", "Ítems disponibles frente a los requeridos", 20, 3),
            ("calificacion", "Calificación del proveedor", "Ranking histórico del proveedor (0-10 estrellas)", 10, 4),
            # Entra en 0 para no alterar los pesos ya configurados (deben sumar 100).
            # El área de compras le asigna su peso desde Comparativo → Pesos de evaluación.
            ("garantia", "Garantía", "Meses de garantía ofrecidos por el proveedor (a más meses, mejor)", 0, 5),
        ]
        for clave, nombre, desc, peso, orden in criterios_base:
            if not db_seed.query(CriterioEvaluacion).filter(CriterioEvaluacion.clave == clave).first():
                db_seed.add(CriterioEvaluacion(
                    clave=clave, nombre=nombre, descripcion=desc, peso_default=peso, orden=orden, activo=True,
                ))
        db_seed.commit()
    finally:
        db_seed.close()

    # Insertar seed data inicial
    db = SessionLocal()
    try:
        seed_initial_data(db)
        seed_example_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="SISA Compras API",
    description="Sistema de gestión de compras y cotizaciones — SISA",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — configurable via env var (default: dev local)
_cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:4201")
cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

# Health check
@app.get(f"{API_PREFIX}/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "service": "sisa-compras-api"}


# Routers
app.include_router(auditoria.router, prefix=API_PREFIX, tags=["Auditoría"])
app.include_router(campos_solicitud.router, prefix=API_PREFIX, tags=["Campos Oportunidad"])
app.include_router(etiquetas.router, prefix=API_PREFIX, tags=["Etiquetas"])
app.include_router(parametros.router, prefix=API_PREFIX, tags=["Parámetros"])
app.include_router(proveedores.router, prefix=API_PREFIX, tags=["Proveedores"])
app.include_router(catalogos.router, prefix=API_PREFIX, tags=["Catálogos"])
app.include_router(solicitudes.router, prefix=API_PREFIX, tags=["Oportunidades"])
app.include_router(cotizaciones.router, prefix=API_PREFIX, tags=["Cotizaciones"])
app.include_router(public.router, prefix=API_PREFIX, tags=["Portal Público"])
app.include_router(dashboard.router, prefix=API_PREFIX, tags=["Dashboard"])
app.include_router(trm.router, prefix=API_PREFIX, tags=["TRM"])
app.include_router(evaluacion.router, prefix=API_PREFIX, tags=["Criterios de Evaluación"])

# Archivos subidos por proveedores (fichas técnicas y PDFs de cotización)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
