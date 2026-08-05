"""
Seed inicial de datos maestros del sistema SISA Compras.
Se ejecuta en el startup de la app solo si las tablas están vacías.
"""
from sqlalchemy.orm import Session

from app.models.etiquetas import Dimension, Etiqueta
from app.models.parametros import UnidadMedida, PlantillaANS, TipoServicio, RubroPresupuestal
from app.models.catalogos import (
    CategoriaProducto,
    DefinicionCampo,
    CategoriaServicio,
    Producto,
    ValorEspecificacion,
    ModeloProducto,
    Servicio,
)
from app.models.proveedores import (
    Proveedor,
    ContactoProveedor,
    EmailContacto,
    TelefonoContacto,
)


def seed_initial_data(db: Session) -> None:
    _seed_unidades_medida(db)
    _seed_plantillas_ans(db)
    _seed_tipos_servicio(db)
    _seed_categorias_producto(db)
    _seed_categorias_servicio(db)
    _seed_rubros_presupuestales(db)


def seed_example_data(db: Session) -> None:
    """Datos de ejemplo funcionales — solo si no hay proveedores cargados."""
    if db.query(Proveedor).first():
        return
    _seed_dimensiones_etiquetas(db)
    _seed_proveedores_ejemplo(db)
    _seed_productos_ejemplo(db)
    _seed_servicios_ejemplo(db)


# ─── Unidades de Medida ───────────────────────────────────────────────────────

def _seed_unidades_medida(db: Session) -> None:
    if db.query(UnidadMedida).first():
        return

    unidades = [
        UnidadMedida(nombre="Gigabyte", simbolo="GB", categoria="almacenamiento"),
        UnidadMedida(nombre="Terabyte", simbolo="TB", categoria="almacenamiento"),
        UnidadMedida(nombre="Petabyte", simbolo="PB", categoria="almacenamiento"),
        UnidadMedida(nombre="Megabyte", simbolo="MB", categoria="almacenamiento"),
        UnidadMedida(nombre="Megahertz", simbolo="MHz", categoria="frecuencia"),
        UnidadMedida(nombre="Gigahertz", simbolo="GHz", categoria="frecuencia"),
        UnidadMedida(nombre="Gigabit por segundo", simbolo="Gbps", categoria="velocidad-red"),
        UnidadMedida(nombre="Terabit por segundo", simbolo="Tbps", categoria="velocidad-red"),
        UnidadMedida(nombre="Watt", simbolo="W", categoria="potencia"),
        UnidadMedida(nombre="Kilovatt", simbolo="kW", categoria="potencia"),
        UnidadMedida(nombre="Tiempo completo equivalente", simbolo="FTE", categoria="recurso-humano"),
        UnidadMedida(nombre="Hora", simbolo="h", categoria="tiempo"),
        UnidadMedida(nombre="Mes", simbolo="mes", categoria="tiempo"),
        UnidadMedida(nombre="Miles", simbolo="K", categoria="escala"),
        UnidadMedida(nombre="Millones", simbolo="M", categoria="escala"),
    ]
    db.add_all(unidades)
    db.commit()


# ─── Plantillas ANS ──────────────────────────────────────────────────────────

def _seed_plantillas_ans(db: Session) -> None:
    if db.query(PlantillaANS).first():
        return

    plantillas = [
        PlantillaANS(nombre="Urgente 4h", horas=4),
        PlantillaANS(nombre="Normal 8h", horas=8),
        PlantillaANS(nombre="Estándar 24h", horas=24),
        PlantillaANS(nombre="Estándar 48h", horas=48),
    ]
    db.add_all(plantillas)
    db.commit()


# ─── Tipos de Servicio ────────────────────────────────────────────────────────

def _seed_tipos_servicio(db: Session) -> None:
    if db.query(TipoServicio).first():
        return

    tipos = [
        TipoServicio(nombre="NOC - Network Operations Center"),
        TipoServicio(nombre="Soporte Especialista"),
        TipoServicio(nombre="IaaS/Cloud"),
        TipoServicio(nombre="Mantenimiento Preventivo"),
        TipoServicio(nombre="Capacitación"),
    ]
    db.add_all(tipos)
    db.commit()


# ─── Categorías de Producto ───────────────────────────────────────────────────

def _seed_categorias_producto(db: Session) -> None:
    if db.query(CategoriaProducto).first():
        return

    categorias_data = [
        {"nombre": "Servidores x86", "slug": "servidores-x86", "tipo": "hardware"},
        {"nombre": "Servidores Power IBM", "slug": "servidores-power-ibm", "tipo": "hardware"},
        {"nombre": "Almacenamiento Flash", "slug": "almacenamiento-flash", "tipo": "hardware"},
        {"nombre": "Memoria RAM", "slug": "memoria-ram", "tipo": "hardware"},
        {"nombre": "Networking", "slug": "networking", "tipo": "hardware"},
        {"nombre": "Soporte Técnico", "slug": "soporte-tecnico", "tipo": "servicio"},
        {"nombre": "Consultoría TI", "slug": "consultoria-ti", "tipo": "servicio"},
        {"nombre": "Mantenimiento Preventivo", "slug": "mantenimiento-preventivo", "tipo": "servicio"},
        {"nombre": "Capacitación y Certificación", "slug": "capacitacion", "tipo": "servicio"},
        {"nombre": "Implementación e Instalación", "slug": "implementacion", "tipo": "servicio"},
        {"nombre": "Software", "slug": "software", "tipo": "software"},
        {"nombre": "Licenciamiento", "slug": "licenciamiento", "tipo": "software"},
        {"nombre": "Sistema Operativo", "slug": "sistema-operativo", "tipo": "software"},
        {"nombre": "Base de Datos", "slug": "base-de-datos", "tipo": "software"},
        {"nombre": "Seguridad y Antivirus", "slug": "seguridad", "tipo": "software"},
        {"nombre": "Colaboración y Productividad", "slug": "colaboracion", "tipo": "software"},
        {"nombre": "ERP y Gestión Empresarial", "slug": "erp", "tipo": "software"},
        {"nombre": "Virtualización y Cloud", "slug": "virtualizacion", "tipo": "software"},
    ]
    categorias = [CategoriaProducto(**data) for data in categorias_data]
    db.add_all(categorias)
    db.flush()

    # Mapa slug → objeto para asignar campos
    cat_map = {c.slug: c for c in categorias}

    # Obtener unidades por símbolo
    def get_unidad(simbolo: str) -> UnidadMedida:
        return db.query(UnidadMedida).filter(UnidadMedida.simbolo == simbolo).first()

    gb = get_unidad("GB")
    tb = get_unidad("TB")
    pb = get_unidad("PB")
    mhz = get_unidad("MHz")
    ghz = get_unidad("GHz")
    gbps = get_unidad("Gbps")
    tbps = get_unidad("Tbps")
    w = get_unidad("W")
    k = get_unidad("K")
    m_esc = get_unidad("M")

    # ── Servidores x86 ─────────────────────────────────────────────────────────
    cat_x86 = cat_map["servidores-x86"]
    campos_x86 = [
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Procesador", clave="cpu", orden=1,
            tipo_dato="texto", tiene_cantidad=True, es_campo_base=True,
            placeholder='ej: Intel Xeon Gold 5418Y (24C/48T)',
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Memoria RAM", clave="ram", orden=2,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=gb.id,
            es_campo_base=True, placeholder="ej: 2048",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Almacenamiento", clave="almacenamiento", orden=3,
            tipo_dato="texto", tiene_cantidad=True, tiene_unidad=True,
            es_campo_base=True, placeholder="ej: NVMe SSD",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Interfaces de red", clave="red", orden=4,
            tipo_dato="texto", es_campo_base=True,
            placeholder="ej: 2× 10GbE + 2× 25GbE",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Fuentes de poder", clave="fuentes", orden=5,
            tipo_dato="numero", tiene_cantidad=True, tiene_unidad=True,
            unidad_default_id=w.id, es_campo_base=True, placeholder="ej: 1800",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Factor de forma", clave="factor_forma", orden=6,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: 2U rack",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_x86.id,
            nombre="Gestión remota", clave="gestion_remota", orden=7,
            tipo_dato="texto", es_campo_base=True,
            placeholder="ej: iDRAC9 Enterprise",
        ),
    ]
    db.add_all(campos_x86)
    db.flush()
    # Asignar unidades a campo ram y almacenamiento
    campos_x86[1].opciones_unidad = [gb, tb]  # ram
    campos_x86[2].opciones_unidad = [gb, tb]  # almacenamiento
    campos_x86[4].opciones_unidad = [w]        # fuentes

    # ── Memoria RAM ────────────────────────────────────────────────────────────
    cat_ram = cat_map["memoria-ram"]
    campos_ram = [
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Capacidad por módulo", clave="capacidad", orden=1,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=gb.id,
            es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Tipo de memoria", clave="tipo", orden=2,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: DDR5 ECC",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Velocidad", clave="velocidad", orden=3,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=mhz.id,
            es_campo_base=True, placeholder="ej: 4800",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Compatible ECC", clave="ecc", orden=4,
            tipo_dato="booleano", es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Factor de forma", clave="factor_forma", orden=5,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: DIMM, RDIMM",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_ram.id,
            nombre="Cantidad de módulos", clave="cantidad_modulos", orden=6,
            tipo_dato="numero", es_campo_base=True, placeholder="ej: 16",
        ),
    ]
    db.add_all(campos_ram)
    db.flush()
    campos_ram[0].opciones_unidad = [gb, tb]
    campos_ram[2].opciones_unidad = [mhz, ghz]

    # ── Almacenamiento Flash ───────────────────────────────────────────────────
    cat_flash = cat_map["almacenamiento-flash"]
    campos_flash = [
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="Capacidad bruta", clave="capacidad_bruta", orden=1,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=tb.id,
            es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="IOPS", clave="iops", orden=2,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=k.id,
            es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="Latencia", clave="latencia", orden=3,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: sub-70μs",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="Interfaces", clave="interfaces", orden=4,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: 32× 32Gb FC",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="Controladoras", clave="controladoras", orden=5,
            tipo_dato="numero", tiene_cantidad=True, es_campo_base=True,
            placeholder="ej: 2 (activo-activo)",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_flash.id,
            nombre="Protocolo", clave="protocolo", orden=6,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: FC, iSCSI, NVMe-oF",
        ),
    ]
    db.add_all(campos_flash)
    db.flush()
    campos_flash[0].opciones_unidad = [tb, pb]
    campos_flash[1].opciones_unidad = [k, m_esc]

    # ── Networking ────────────────────────────────────────────────────────────
    cat_net = cat_map["networking"]
    campos_net = [
        DefinicionCampo(
            categoria_producto_id=cat_net.id,
            nombre="Puertos", clave="puertos", orden=1,
            tipo_dato="texto", es_campo_base=True,
            placeholder="ej: 48×25GbE + 8×100GbE",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_net.id,
            nombre="Capacidad switching", clave="switching", orden=2,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=gbps.id,
            es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_net.id,
            nombre="Latencia", clave="latencia", orden=3,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: 300ns",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_net.id,
            nombre="Factor de forma", clave="factor_forma", orden=4,
            tipo_dato="texto", es_campo_base=True, placeholder="ej: 1U",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_net.id,
            nombre="Gestión", clave="gestion", orden=5,
            tipo_dato="texto", es_campo_base=True,
            placeholder="ej: RESTCONF, NETCONF, GUI",
        ),
    ]
    db.add_all(campos_net)
    db.flush()
    campos_net[1].opciones_unidad = [gbps, tbps]

    # ── Servidores Power IBM ───────────────────────────────────────────────────
    cat_power = cat_map["servidores-power-ibm"]
    campos_power = [
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Modelo", clave="modelo", orden=1,
            tipo_dato="texto", es_obligatorio=True, es_campo_base=True,
            placeholder="ej: IBM Power S1022",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Procesadores", clave="procesadores", orden=2,
            tipo_dato="texto", tiene_cantidad=True, es_campo_base=True,
            placeholder="ej: IBM POWER10",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Memoria RAM", clave="ram", orden=3,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=gb.id,
            es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Almacenamiento", clave="almacenamiento", orden=4,
            tipo_dato="texto", es_campo_base=True,
        ),
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Sistema operativo", clave="os", orden=5,
            tipo_dato="texto", es_campo_base=True,
            placeholder="ej: AIX, IBM i, Linux",
        ),
        DefinicionCampo(
            categoria_producto_id=cat_power.id,
            nombre="Slots de expansión", clave="expansion", orden=6,
            tipo_dato="numero", es_campo_base=True,
        ),
    ]
    db.add_all(campos_power)
    db.flush()
    campos_power[2].opciones_unidad = [gb, tb]

    h = get_unidad("h")
    mes = get_unidad("mes")
    fte = get_unidad("FTE")

    # ── Soporte Técnico ────────────────────────────────────────────────────────
    cat_sop = cat_map["soporte-tecnico"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Nivel de soporte", clave="nivel", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: L1 / L2 / L3"),
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Disponibilidad", clave="disponibilidad", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: 8×5 / 12×5 / 24×7"),
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Modalidad", clave="modalidad", orden=3,
            tipo_dato="texto", placeholder="ej: Presencial / Remoto / Híbrido"),
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Tiempo de respuesta", clave="tiempo_respuesta", orden=4,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=h.id, placeholder="ej: 4"),
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Perfil técnico requerido", clave="perfil", orden=5,
            tipo_dato="texto", placeholder="ej: Ingeniero CCNA / RHCE"),
        DefinicionCampo(categoria_producto_id=cat_sop.id, nombre="Cobertura geográfica", clave="cobertura", orden=6,
            tipo_dato="texto", placeholder="ej: Bogotá DC / Nacional"),
    ])
    db.flush()

    # ── Consultoría TI ────────────────────────────────────────────────────────
    cat_con = cat_map["consultoria-ti"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_con.id, nombre="Área de consultoría", clave="area", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Seguridad / Cloud / Datos"),
        DefinicionCampo(categoria_producto_id=cat_con.id, nombre="Modalidad", clave="modalidad", orden=2,
            tipo_dato="texto", placeholder="ej: Presencial / Remoto"),
        DefinicionCampo(categoria_producto_id=cat_con.id, nombre="Duración estimada", clave="duracion", orden=3,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=mes.id, placeholder="ej: 3"),
        DefinicionCampo(categoria_producto_id=cat_con.id, nombre="Perfil requerido", clave="perfil", orden=4,
            tipo_dato="texto", placeholder="ej: Arquitecto de Soluciones"),
        DefinicionCampo(categoria_producto_id=cat_con.id, nombre="Entregables", clave="entregables", orden=5,
            tipo_dato="texto", placeholder="ej: Informe de diagnóstico, Roadmap"),
    ])
    db.flush()
    c_dur = db.query(DefinicionCampo).filter(DefinicionCampo.categoria_producto_id == cat_con.id, DefinicionCampo.clave == "duracion").first()
    if c_dur: c_dur.opciones_unidad = [h, mes]
    db.flush()

    # ── Mantenimiento Preventivo ──────────────────────────────────────────────
    cat_mnt = cat_map["mantenimiento-preventivo"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_mnt.id, nombre="Frecuencia", clave="frecuencia", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Mensual / Trimestral / Semestral"),
        DefinicionCampo(categoria_producto_id=cat_mnt.id, nombre="Equipos a cubrir", clave="equipos", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Servidores Dell PowerEdge R760 ×5"),
        DefinicionCampo(categoria_producto_id=cat_mnt.id, nombre="Ventana de mantenimiento", clave="ventana", orden=3,
            tipo_dato="texto", placeholder="ej: Sábados 02:00 – 06:00"),
        DefinicionCampo(categoria_producto_id=cat_mnt.id, nombre="Tipo de cobertura", clave="cobertura", orden=4,
            tipo_dato="texto", placeholder="ej: Hardware + Software + Firmware"),
        DefinicionCampo(categoria_producto_id=cat_mnt.id, nombre="Modalidad", clave="modalidad", orden=5,
            tipo_dato="texto", placeholder="ej: On-site / Remoto"),
    ])
    db.flush()

    # ── Capacitación y Certificación ──────────────────────────────────────────
    cat_cap = cat_map["capacitacion"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_cap.id, nombre="Curso / Certificación", clave="curso", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: RHCSA / CCNA / AWS Solutions Architect"),
        DefinicionCampo(categoria_producto_id=cat_cap.id, nombre="Modalidad", clave="modalidad", orden=2,
            tipo_dato="texto", placeholder="ej: Presencial / Virtual / Blended"),
        DefinicionCampo(categoria_producto_id=cat_cap.id, nombre="Duración", clave="duracion", orden=3,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=h.id, placeholder="ej: 40"),
        DefinicionCampo(categoria_producto_id=cat_cap.id, nombre="Número de participantes", clave="participantes", orden=4,
            tipo_dato="numero", placeholder="ej: 10"),
        DefinicionCampo(categoria_producto_id=cat_cap.id, nombre="Proveedor autorizado", clave="proveedor_cert", orden=5,
            tipo_dato="texto", placeholder="ej: Red Hat / Cisco / AWS"),
    ])
    db.flush()
    c_dur2 = db.query(DefinicionCampo).filter(DefinicionCampo.categoria_producto_id == cat_cap.id, DefinicionCampo.clave == "duracion").first()
    if c_dur2: c_dur2.opciones_unidad = [h]
    db.flush()

    # ── Implementación e Instalación ──────────────────────────────────────────
    cat_imp = cat_map["implementacion"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_imp.id, nombre="Tecnología / Plataforma", clave="tecnologia", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: VMware vSphere 8 / SAP HANA"),
        DefinicionCampo(categoria_producto_id=cat_imp.id, nombre="Alcance", clave="alcance", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Instalación + configuración + pruebas"),
        DefinicionCampo(categoria_producto_id=cat_imp.id, nombre="Modalidad", clave="modalidad", orden=3,
            tipo_dato="texto", placeholder="ej: On-site / Remoto"),
        DefinicionCampo(categoria_producto_id=cat_imp.id, nombre="Horas estimadas", clave="horas", orden=4,
            tipo_dato="numero", tiene_unidad=True, unidad_default_id=h.id, placeholder="ej: 80"),
        DefinicionCampo(categoria_producto_id=cat_imp.id, nombre="Entregables", clave="entregables", orden=5,
            tipo_dato="texto", placeholder="ej: As-built, Manual de operación"),
    ])
    db.flush()
    c_h = db.query(DefinicionCampo).filter(DefinicionCampo.categoria_producto_id == cat_imp.id, DefinicionCampo.clave == "horas").first()
    if c_h: c_h.opciones_unidad = [h]
    db.flush()

    # ── Sistema Operativo ─────────────────────────────────────────────────────
    cat_so = cat_map["sistema-operativo"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_so.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Red Hat / Microsoft / Ubuntu"),
        DefinicionCampo(categoria_producto_id=cat_so.id, nombre="Nombre y versión", clave="nombre_version", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: RHEL 9.3 / Windows Server 2022"),
        DefinicionCampo(categoria_producto_id=cat_so.id, nombre="Tipo de licencia", clave="tipo_licencia", orden=3,
            tipo_dato="texto", placeholder="ej: OEM / Retail / Volume / Suscripción"),
        DefinicionCampo(categoria_producto_id=cat_so.id, nombre="Arquitectura", clave="arquitectura", orden=4,
            tipo_dato="texto", placeholder="ej: x86_64 / ARM / POWER"),
        DefinicionCampo(categoria_producto_id=cat_so.id, nombre="Vigencia", clave="vigencia", orden=5,
            tipo_dato="texto", placeholder="ej: 1 año / 3 años / Perpetua"),
    ])
    db.flush()

    # ── Base de Datos ─────────────────────────────────────────────────────────
    cat_bd = cat_map["base-de-datos"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Oracle / Microsoft / PostgreSQL"),
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Nombre y versión", clave="nombre_version", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Oracle DB 19c Enterprise"),
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Edición", clave="edicion", orden=3,
            tipo_dato="texto", placeholder="ej: Standard / Enterprise / Express"),
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Tipo de licencia", clave="tipo_licencia", orden=4,
            tipo_dato="texto", placeholder="ej: Perpetua / Suscripción / CAL / Por procesador"),
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Número de usuarios/cores", clave="usuarios_cores", orden=5,
            tipo_dato="numero", placeholder="ej: 25"),
        DefinicionCampo(categoria_producto_id=cat_bd.id, nombre="Vigencia", clave="vigencia", orden=6,
            tipo_dato="texto", placeholder="ej: 1 año / Perpetua"),
    ])
    db.flush()

    # ── Seguridad y Antivirus ─────────────────────────────────────────────────
    cat_seg = cat_map["seguridad"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_seg.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Symantec / Kaspersky / CrowdStrike"),
        DefinicionCampo(categoria_producto_id=cat_seg.id, nombre="Producto", clave="producto", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Endpoint Security / EDR"),
        DefinicionCampo(categoria_producto_id=cat_seg.id, nombre="Número de endpoints", clave="endpoints", orden=3,
            tipo_dato="numero", es_obligatorio=True, placeholder="ej: 500"),
        DefinicionCampo(categoria_producto_id=cat_seg.id, nombre="Vigencia", clave="vigencia", orden=4,
            tipo_dato="texto", placeholder="ej: 1 año / 2 años / 3 años"),
        DefinicionCampo(categoria_producto_id=cat_seg.id, nombre="Modalidad de despliegue", clave="modalidad", orden=5,
            tipo_dato="texto", placeholder="ej: Cloud / On-premise / Híbrido"),
    ])
    db.flush()

    # ── Colaboración y Productividad ──────────────────────────────────────────
    cat_col = cat_map["colaboracion"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_col.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Microsoft / Google / Atlassian"),
        DefinicionCampo(categoria_producto_id=cat_col.id, nombre="Suite / Producto", clave="suite", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: Microsoft 365 E3 / Google Workspace"),
        DefinicionCampo(categoria_producto_id=cat_col.id, nombre="Número de usuarios", clave="usuarios", orden=3,
            tipo_dato="numero", es_obligatorio=True, placeholder="ej: 150"),
        DefinicionCampo(categoria_producto_id=cat_col.id, nombre="Vigencia", clave="vigencia", orden=4,
            tipo_dato="texto", placeholder="ej: Anual / Mensual"),
        DefinicionCampo(categoria_producto_id=cat_col.id, nombre="Modalidad", clave="modalidad", orden=5,
            tipo_dato="texto", placeholder="ej: Cloud / On-premise"),
    ])
    db.flush()

    # ── ERP y Gestión Empresarial ─────────────────────────────────────────────
    cat_erp = cat_map["erp"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_erp.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: SAP / Oracle / Microsoft"),
        DefinicionCampo(categoria_producto_id=cat_erp.id, nombre="Producto y módulos", clave="producto_modulos", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: SAP S/4HANA – FI, MM, SD"),
        DefinicionCampo(categoria_producto_id=cat_erp.id, nombre="Número de usuarios", clave="usuarios", orden=3,
            tipo_dato="numero", es_obligatorio=True, placeholder="ej: 50"),
        DefinicionCampo(categoria_producto_id=cat_erp.id, nombre="Modalidad", clave="modalidad", orden=4,
            tipo_dato="texto", placeholder="ej: Cloud / On-premise / Híbrido"),
        DefinicionCampo(categoria_producto_id=cat_erp.id, nombre="Vigencia", clave="vigencia", orden=5,
            tipo_dato="texto", placeholder="ej: Anual / Perpetua"),
    ])
    db.flush()

    # ── Virtualización y Cloud ────────────────────────────────────────────────
    cat_virt = cat_map["virtualizacion"]
    db.add_all([
        DefinicionCampo(categoria_producto_id=cat_virt.id, nombre="Fabricante", clave="fabricante", orden=1,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: VMware / Microsoft / Nutanix"),
        DefinicionCampo(categoria_producto_id=cat_virt.id, nombre="Plataforma", clave="plataforma", orden=2,
            tipo_dato="texto", es_obligatorio=True, placeholder="ej: vSphere 8 / Hyper-V / AHV"),
        DefinicionCampo(categoria_producto_id=cat_virt.id, nombre="Tipo de licencia", clave="tipo_licencia", orden=3,
            tipo_dato="texto", placeholder="ej: Per Socket / Per Core / Suscripción"),
        DefinicionCampo(categoria_producto_id=cat_virt.id, nombre="Número de sockets/VMs", clave="sockets_vms", orden=4,
            tipo_dato="numero", placeholder="ej: 8"),
        DefinicionCampo(categoria_producto_id=cat_virt.id, nombre="Vigencia", clave="vigencia", orden=5,
            tipo_dato="texto", placeholder="ej: 1 año / 3 años / Perpetua"),
    ])
    db.flush()

    db.commit()


# ─── Categorías de Servicio ───────────────────────────────────────────────────

def _seed_categorias_servicio(db: Session) -> None:
    if db.query(CategoriaServicio).first():
        return

    categorias = [
        CategoriaServicio(
            nombre="Operaciones",
            descripcion="Servicios de operación 24×7",
        ),
        CategoriaServicio(
            nombre="Soporte Técnico",
            descripcion="Soporte especializado en infraestructura",
        ),
        CategoriaServicio(
            nombre="Cloud e IaaS",
            descripcion="Servicios de nube y hosting",
        ),
        CategoriaServicio(
            nombre="Capacitación",
            descripcion="Entrenamientos y certificaciones",
        ),
    ]
    db.add_all(categorias)
    db.commit()


# ─── Datos de Ejemplo ─────────────────────────────────────────────────────────

def _seed_dimensiones_etiquetas(db: Session) -> None:
    dim_marca = Dimension(nombre="Marca", color="#0077C8", descripcion="Fabricante del producto")
    dim_tipo = Dimension(nombre="Tipo de equipo", color="#28a745", descripcion="Categoría de hardware")
    dim_pais = Dimension(nombre="País", color="#6c757d", descripcion="País de origen del proveedor")
    db.add_all([dim_marca, dim_tipo, dim_pais])
    db.flush()

    etiquetas = [
        Etiqueta(nombre="Dell", color="#007DB8", dimension_id=dim_marca.id),
        Etiqueta(nombre="HPE", color="#01A982", dimension_id=dim_marca.id),
        Etiqueta(nombre="IBM", color="#1F70C1", dimension_id=dim_marca.id),
        Etiqueta(nombre="Cisco", color="#049FD9", dimension_id=dim_marca.id),
        Etiqueta(nombre="Servidores", color="#17a2b8", dimension_id=dim_tipo.id),
        Etiqueta(nombre="Almacenamiento", color="#6610f2", dimension_id=dim_tipo.id),
        Etiqueta(nombre="Networking", color="#fd7e14", dimension_id=dim_tipo.id),
        Etiqueta(nombre="Colombia", color="#ffc107", dimension_id=dim_pais.id),
        Etiqueta(nombre="USA", color="#dc3545", dimension_id=dim_pais.id),
    ]
    db.add_all(etiquetas)
    db.commit()


def _seed_proveedores_ejemplo(db: Session) -> None:
    tag_colombia = db.query(Etiqueta).filter(Etiqueta.nombre == "Colombia").first()
    tag_usa = db.query(Etiqueta).filter(Etiqueta.nombre == "USA").first()
    tag_dell = db.query(Etiqueta).filter(Etiqueta.nombre == "Dell").first()
    tag_hpe = db.query(Etiqueta).filter(Etiqueta.nombre == "HPE").first()
    tag_serv = db.query(Etiqueta).filter(Etiqueta.nombre == "Servidores").first()
    tag_net = db.query(Etiqueta).filter(Etiqueta.nombre == "Networking").first()

    # Proveedor 1 — Bytestock SAS (Colombia)
    bytestock = Proveedor(
        razon_social="Bytestock SAS",
        nombre_comercial="Bytestock",
        pais="Colombia",
        idioma="ES",
        sitio_web="https://bytestock.com.co",
        estado="activo",
        notas="Proveedor local especializado en memoria RAM y SSDs. Respuesta en 24h.",
    )
    bytestock.etiquetas = [tag_colombia, tag_hpe]
    db.add(bytestock)
    db.flush()

    contacto_bs = ContactoProveedor(
        proveedor_id=bytestock.id, nombre="Carlos Mora", cargo="Ejecutivo Comercial", es_principal=True
    )
    db.add(contacto_bs)
    db.flush()
    db.add(EmailContacto(contacto_id=contacto_bs.id, email="cmora@bytestock.com.co", tipo="comercial", es_principal=True))
    db.add(TelefonoContacto(contacto_id=contacto_bs.id, numero="+57 300 555 1234", tipo="celular"))
    db.add(TelefonoContacto(contacto_id=contacto_bs.id, numero="+57 1 555 0000", tipo="fijo", extension="205"))

    # Proveedor 2 — ETB (Colombia)
    etb = Proveedor(
        razon_social="Empresa de Telecomunicaciones de Bogotá S.A. E.S.P.",
        nombre_comercial="ETB",
        pais="Colombia",
        idioma="ES",
        sitio_web="https://www.etb.com.co",
        estado="activo",
        notas="Proveedor de conectividad y servicios cloud. Priorizar para servicios IaaS.",
    )
    etb.etiquetas = [tag_colombia]
    db.add(etb)
    db.flush()

    contacto_etb = ContactoProveedor(
        proveedor_id=etb.id, nombre="Lucía Restrepo", cargo="Gerente de Cuentas", es_principal=True
    )
    db.add(contacto_etb)
    db.flush()
    db.add(EmailContacto(contacto_id=contacto_etb.id, email="lrestrepo@etb.com.co", tipo="comercial", es_principal=True))
    db.add(TelefonoContacto(contacto_id=contacto_etb.id, numero="+57 1 888 0000", tipo="fijo", extension="312"))

    # Proveedor 3 — Dell Technologies (USA, EN)
    dell = Proveedor(
        razon_social="Dell Technologies Inc.",
        nombre_comercial="Dell",
        pais="USA",
        idioma="EN",
        sitio_web="https://www.dell.com",
        estado="activo",
        notas="Main channel for PowerEdge servers and PowerStore. Lead time: 8-12 weeks import.",
    )
    dell.etiquetas = [tag_usa, tag_dell, tag_serv]
    db.add(dell)
    db.flush()

    contacto_dell = ContactoProveedor(
        proveedor_id=dell.id, nombre="John Ramirez", cargo="Latin America Channel Manager", es_principal=True
    )
    db.add(contacto_dell)
    db.flush()
    db.add(EmailContacto(contacto_id=contacto_dell.id, email="john.ramirez@dell.com", tipo="comercial", es_principal=True))
    db.add(EmailContacto(contacto_id=contacto_dell.id, email="latam-quotes@dell.com", tipo="comercial", es_principal=False))
    db.add(TelefonoContacto(contacto_id=contacto_dell.id, numero="+1 800 624 9897", tipo="fijo"))

    # Proveedor 4 — Cisco Systems (USA, EN)
    cisco = Proveedor(
        razon_social="Cisco Systems Inc.",
        nombre_comercial="Cisco",
        pais="USA",
        idioma="EN",
        sitio_web="https://www.cisco.com",
        estado="activo",
        notas="Networking infrastructure. Quotes via authorized reseller channel.",
    )
    cisco.etiquetas = [tag_usa, tag_net]
    db.add(cisco)
    db.flush()

    contacto_cisco = ContactoProveedor(
        proveedor_id=cisco.id, nombre="Maria Lopez", cargo="Regional Sales", es_principal=True
    )
    db.add(contacto_cisco)
    db.flush()
    db.add(EmailContacto(contacto_id=contacto_cisco.id, email="m.lopez@cisco.com", tipo="comercial", es_principal=True))

    db.commit()


def _seed_productos_ejemplo(db: Session) -> None:
    cat_x86 = db.query(CategoriaProducto).filter(CategoriaProducto.slug == "servidores-x86").first()
    cat_ram = db.query(CategoriaProducto).filter(CategoriaProducto.slug == "memoria-ram").first()
    cat_net = db.query(CategoriaProducto).filter(CategoriaProducto.slug == "networking").first()

    tag_dell = db.query(Etiqueta).filter(Etiqueta.nombre == "Dell").first()
    tag_hpe = db.query(Etiqueta).filter(Etiqueta.nombre == "HPE").first()
    tag_cisco = db.query(Etiqueta).filter(Etiqueta.nombre == "Cisco").first()
    tag_serv = db.query(Etiqueta).filter(Etiqueta.nombre == "Servidores").first()
    tag_net = db.query(Etiqueta).filter(Etiqueta.nombre == "Networking").first()

    gb = db.query(UnidadMedida).filter(UnidadMedida.simbolo == "GB").first()
    tb = db.query(UnidadMedida).filter(UnidadMedida.simbolo == "TB").first()
    w = db.query(UnidadMedida).filter(UnidadMedida.simbolo == "W").first()

    # ── Producto 1: Dell PowerEdge R760 ──────────────────────────────────────
    r760 = Producto(
        nombre="Servidor Rack Dell PowerEdge R760",
        descripcion="Servidor 2U de doble socket para cargas de trabajo empresariales. Soporta hasta 8 TB de RAM DDR5.",
        categoria_producto_id=cat_x86.id,
        modo_defecto="modelos_especificos",
        fabricante="Dell Technologies",
        activo=True,
    )
    r760.etiquetas = [tag_dell, tag_serv]
    db.add(r760)
    db.flush()

    # Modelos alternativos
    db.add_all([
        ModeloProducto(producto_id=r760.id, fabricante="Dell", modelo="PowerEdge R760", es_primario=True, orden=1),
        ModeloProducto(producto_id=r760.id, fabricante="HPE", modelo="ProLiant DL380 Gen11", es_primario=False, orden=2),
        ModeloProducto(producto_id=r760.id, fabricante="Lenovo", modelo="ThinkSystem SR650 V3", es_primario=False, orden=3),
    ])

    # Specs
    campo_cpu = db.query(DefinicionCampo).filter(
        DefinicionCampo.categoria_producto_id == cat_x86.id,
        DefinicionCampo.clave == "cpu"
    ).first()
    campo_ram = db.query(DefinicionCampo).filter(
        DefinicionCampo.categoria_producto_id == cat_x86.id,
        DefinicionCampo.clave == "ram"
    ).first()
    campo_ff = db.query(DefinicionCampo).filter(
        DefinicionCampo.categoria_producto_id == cat_x86.id,
        DefinicionCampo.clave == "factor_forma"
    ).first()
    campo_mgmt = db.query(DefinicionCampo).filter(
        DefinicionCampo.categoria_producto_id == cat_x86.id,
        DefinicionCampo.clave == "gestion_remota"
    ).first()

    if campo_cpu:
        db.add(ValorEspecificacion(producto_id=r760.id, campo_id=campo_cpu.id, cantidad=2, valor="Intel Xeon Gold 5418Y (24C/48T, 2.0GHz)"))
    if campo_ram:
        db.add(ValorEspecificacion(producto_id=r760.id, campo_id=campo_ram.id, valor="2048", unidad_medida_id=gb.id))
    if campo_ff:
        db.add(ValorEspecificacion(producto_id=r760.id, campo_id=campo_ff.id, valor="2U rack"))
    if campo_mgmt:
        db.add(ValorEspecificacion(producto_id=r760.id, campo_id=campo_mgmt.id, valor="iDRAC9 Enterprise"))

    # ── Producto 2: Módulo RAM Kingston 64GB DDR5 ────────────────────────────
    if cat_ram:
        ram64 = Producto(
            nombre="Módulo RAM 64GB DDR5 ECC RDIMM",
            descripcion="Memoria RAM de servidor compatible con Intel Xeon 4ta gen. Certificada para Dell PowerEdge y HPE ProLiant.",
            categoria_producto_id=cat_ram.id,
            modo_defecto="funcional",
            fabricante="Kingston",
            activo=True,
        )
        ram64.etiquetas = [tag_hpe]
        db.add(ram64)
        db.flush()

        c_cap = db.query(DefinicionCampo).filter(
            DefinicionCampo.categoria_producto_id == cat_ram.id,
            DefinicionCampo.clave == "capacidad"
        ).first()
        c_tipo = db.query(DefinicionCampo).filter(
            DefinicionCampo.categoria_producto_id == cat_ram.id,
            DefinicionCampo.clave == "tipo"
        ).first()
        c_ecc = db.query(DefinicionCampo).filter(
            DefinicionCampo.categoria_producto_id == cat_ram.id,
            DefinicionCampo.clave == "ecc"
        ).first()
        if c_cap:
            db.add(ValorEspecificacion(producto_id=ram64.id, campo_id=c_cap.id, valor="64", unidad_medida_id=gb.id))
        if c_tipo:
            db.add(ValorEspecificacion(producto_id=ram64.id, campo_id=c_tipo.id, valor="DDR5 ECC RDIMM"))
        if c_ecc:
            db.add(ValorEspecificacion(producto_id=ram64.id, campo_id=c_ecc.id, valor="true"))

    db.commit()


def _seed_servicios_ejemplo(db: Session) -> None:
    cat_ops = db.query(CategoriaServicio).filter(CategoriaServicio.nombre == "Operaciones").first()
    cat_sop = db.query(CategoriaServicio).filter(CategoriaServicio.nombre == "Soporte Técnico").first()
    tipo_noc = db.query(TipoServicio).filter(TipoServicio.nombre == "NOC - Network Operations Center").first()
    tipo_esp = db.query(TipoServicio).filter(TipoServicio.nombre == "Soporte Especialista").first()
    unidad_h = db.query(UnidadMedida).filter(UnidadMedida.simbolo == "h").first()
    unidad_fte = db.query(UnidadMedida).filter(UnidadMedida.simbolo == "FTE").first()

    servicios = [
        Servicio(
            nombre="Soporte NOC 24×7",
            descripcion="Monitoreo proactivo de infraestructura con mesa de ayuda disponible 24 horas los 7 días.",
            categoria_servicio_id=cat_ops.id if cat_ops else None,
            tipo_servicio_id=tipo_noc.id if tipo_noc else None,
            unidad_medida_id=unidad_h.id if unidad_h else None,
            activo=True,
        ),
        Servicio(
            nombre="Especialista en Infraestructura On-Site",
            descripcion="Ingeniero especializado en datacenter disponible en sitio. Cubre servidores x86, storage y networking.",
            categoria_servicio_id=cat_sop.id if cat_sop else None,
            tipo_servicio_id=tipo_esp.id if tipo_esp else None,
            unidad_medida_id=unidad_fte.id if unidad_fte else None,
            activo=True,
        ),
    ]
    db.add_all(servicios)
    db.commit()


# ─── Rubros Presupuestales ────────────────────────────────────────────────────

def _seed_rubros_presupuestales(db: Session) -> None:
    if db.query(RubroPresupuestal).first():
        return

    rubros = [
        RubroPresupuestal(nombre="Tecnología e Infraestructura", codigo="TEC-001", activo=True),
        RubroPresupuestal(nombre="Software y Licencias", codigo="TEC-002", activo=True),
        RubroPresupuestal(nombre="Servicios Profesionales", codigo="SVC-001", activo=True),
        RubroPresupuestal(nombre="Mantenimiento y Soporte", codigo="SVC-002", activo=True),
        RubroPresupuestal(nombre="Equipos y Suministros", codigo="ADM-001", activo=True),
        RubroPresupuestal(nombre="Comunicaciones", codigo="TEC-003", activo=True),
    ]
    db.add_all(rubros)
    db.commit()
