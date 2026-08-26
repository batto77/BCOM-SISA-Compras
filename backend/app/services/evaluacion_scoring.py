"""Motor de puntuación para la adjudicación del proveedor ganador.

La comparación se hace **por ítem** (manzana con manzana): para cada ítem
requerido se compara el precio unitario, el tiempo de entrega y la calificación
de los proveedores que sí lo ofertan, y se sugiere el mejor proveedor de ese ítem.
La compra puede repartirse (adjudicación por ítem).

Todos los precios se normalizan a la moneda de la oportunidad para cálculos
consistentes. Se retornan tanto valores originales como convertidos.

Además se calcula un **ranking global corregido**: el criterio financiero usa
precios convertidos a la moneda de la oportunidad, promediados sobre TODOS los
ítems requeridos (los que no se ofertan cuentan como 0, penalizando cobertura
parcial).

Sub-puntajes (0–100):
  - financiero     : mejor_precio_ítem / precio_del_proveedor × 100  (por ítem, usando valores convertidos)
  - tiempo_entrega : menor_días_ítem / días_del_proveedor × 100      (por ítem)
  - garantia       : meses_del_proveedor / mayor_garantía_ítem × 100 (por ítem; a más meses, mejor)
  - completitud    : ítems ofertados / ítems requeridos × 100        (solo global)
  - calificacion   : calificación_del_proveedor (0–10) × 10
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

CLAVES = ("financiero", "tiempo_entrega", "garantia", "completitud", "calificacion")
CLAVES_ITEM = ("financiero", "tiempo_entrega", "garantia", "calificacion")


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def _item_lookup(cot) -> Dict[int, Any]:
    """Map item_solicitud_id -> ItemCotizacion, solo disponibles y con precio > 0."""
    m: Dict[int, Any] = {}
    for it in cot.items:
        if it.item_solicitud_id is None:
            continue
        if it.disponible and _num(it.precio_unitario) > 0:
            m[it.item_solicitud_id] = it
    return m


def _obtener_precio_convertido(
    db: Session,
    precio_original: float,
    moneda_cotizacion: str,
    moneda_oportunidad: str
) -> float:
    """Convierte un precio de la moneda de cotización a la moneda de la oportunidad."""
    if moneda_cotizacion.upper() == moneda_oportunidad.upper():
        return precio_original

    # Importar aquí para evitar circular imports
    from app.services.conversion import convertir_a_cop, obtener_tasa_cambio

    if moneda_oportunidad.upper() == "COP":
        return _num(convertir_a_cop(db, Decimal(precio_original), moneda_cotizacion))

    # Convertir a COP y luego a la moneda de destino
    en_cop = _num(convertir_a_cop(db, Decimal(precio_original), moneda_cotizacion))
    if moneda_oportunidad.upper() == "COP":
        return en_cop
    tasa_destino = _num(obtener_tasa_cambio(db, moneda_oportunidad))
    if tasa_destino > 0:
        return en_cop / tasa_destino
    return precio_original


def resolver_pesos(pesos_solicitud: Optional[dict], criterios_base: List[Any]) -> Dict[str, float]:
    """Combina los pesos base (tabla paramétrica) con el override de la oportunidad."""
    pesos: Dict[str, float] = {}
    for c in criterios_base:
        if getattr(c, "activo", True):
            pesos[c.clave] = _num(c.peso_default)
    if pesos_solicitud:
        for clave, valor in pesos_solicitud.items():
            if clave in pesos or clave in CLAVES:
                pesos[clave] = _num(valor)
    return pesos


def _score_tiempo(dias: Optional[int], menor_dias: float) -> float:
    if dias is None:
        return 0.0
    if dias <= 0:
        return 100.0
    if menor_dias > 0:
        return round(menor_dias / dias * 100, 1)
    return 0.0


def _score_garantia(meses: Optional[int], mayor_meses: float) -> float:
    """A diferencia de precio y tiempo, acá **más es mejor**.

    0 meses (o sin dato) = no aplica = 0 puntos. Si nadie ofrece garantía en el
    ítem, todos quedan en 0 y el criterio no desempata.
    """
    if not meses or meses <= 0:
        return 0.0
    if mayor_meses > 0:
        return round(min(meses / mayor_meses, 1.0) * 100, 1)
    return 0.0


def calcular_evaluacion(
    *,
    db: Session,
    items_solicitud: List[Any],
    cotizaciones: List[Any],
    pesos: Dict[str, float],
    moneda_oportunidad: str = "COP",
) -> Dict[str, Any]:
    """Devuelve la evaluación por ítem + ranking global + adjudicación sugerida.

    Todos los precios se normalizan a la moneda de la oportunidad.
    Solo participan las cotizaciones en estado 'respondida'.
    """
    respondidas = [c for c in cotizaciones if c.estado == "respondida"]
    total_items = len(items_solicitud)
    lookups = {c.id: _item_lookup(c) for c in respondidas}
    cant = {i.id: (_num(getattr(i, "cantidad", 1)) or 1) for i in items_solicitud}

    # Mejor precio y menor tiempo por ítem (usando valores convertidos)
    mejor_precio: Dict[int, float] = {}
    menor_dias: Dict[int, float] = {}
    mayor_garantia: Dict[int, float] = {}
    precios_por_item: Dict[int, Dict[int, Dict]] = {}  # item_id -> cot_id -> {original, convertido, moneda}

    for i in items_solicitud:
        precios_convertidos, dias_list, garantias_list = [], [], []
        precios_por_item[i.id] = {}

        for c in respondidas:
            it = lookups[c.id].get(i.id)
            if it:
                precio_original = _num(it.precio_unitario)
                moneda_cot = getattr(c, "moneda", "COP")
                precio_convertido = _obtener_precio_convertido(
                    db, precio_original, moneda_cot, moneda_oportunidad
                )
                precios_convertidos.append(precio_convertido)
                precios_por_item[i.id][c.id] = {
                    "precio_original": precio_original,
                    "moneda_original": moneda_cot,
                    "precio_convertido": precio_convertido,
                }
                if it.tiempo_entrega_dias is not None:
                    dias_list.append(it.tiempo_entrega_dias)
                garantia = getattr(it, "garantia_meses", None)
                if garantia:
                    garantias_list.append(garantia)

        mejor_precio[i.id] = min(precios_convertidos) if precios_convertidos else 0.0
        menor_dias[i.id] = min(dias_list) if dias_list else 0.0
        mayor_garantia[i.id] = max(garantias_list) if garantias_list else 0.0

    # Pesos por ítem (sin completitud), renormalizados
    pesos_item = {k: pesos.get(k, 0) for k in CLAVES_ITEM}
    suma_pesos_item = sum(pesos_item.values()) or 1

    # ---- Evaluación por ítem (adjudicación) ----
    por_item = []
    adjudicacion_sugerida: Dict[int, int] = {}

    for i in items_solicitud:
        candidatos = []
        for c in respondidas:
            it = lookups[c.id].get(i.id)
            if not it:
                continue

            # Usar valores convertidos para cálculos
            precio_info = precios_por_item[i.id].get(c.id, {})
            precio_original = precio_info.get("precio_original", 0.0)
            moneda_original = precio_info.get("moneda_original", "COP")
            precio_convertido = precio_info.get("precio_convertido", 0.0)

            s_fin = (
                round(mejor_precio[i.id] / precio_convertido * 100, 1)
                if precio_convertido > 0 and mejor_precio[i.id] > 0
                else 0.0
            )
            s_time = _score_tiempo(it.tiempo_entrega_dias, menor_dias[i.id])
            garantia_meses = getattr(it, "garantia_meses", None) or 0
            s_gar = _score_garantia(garantia_meses, mayor_garantia[i.id])
            s_cal = round(_num(getattr(c.proveedor, "calificacion", None)) * 10, 1) if c.proveedor else 0.0

            final = (
                s_fin * pesos_item["financiero"]
                + s_time * pesos_item["tiempo_entrega"]
                + s_gar * pesos_item["garantia"]
                + s_cal * pesos_item["calificacion"]
            ) / suma_pesos_item

            candidatos.append({
                "cotizacion_id": c.id,
                "proveedor_id": c.proveedor_id,
                "precio_unitario_original": precio_original,
                "moneda_original": moneda_original,
                "precio_unitario_convertido": precio_convertido,
                "cantidad": cant.get(i.id, 1),
                "subtotal_original": precio_original * cant.get(i.id, 1),
                "subtotal_convertido": precio_convertido * cant.get(i.id, 1),
                "tiempo_entrega_dias": it.tiempo_entrega_dias,
                "garantia_meses": garantia_meses,
                "subpuntajes": {
                    "financiero": s_fin,
                    "tiempo_entrega": s_time,
                    "garantia": s_gar,
                    "calificacion": s_cal,
                },
                "puntaje": round(final, 1),
                "es_mejor": False,
            })

        mejor_id = None
        if candidatos:
            mejor = max(candidatos, key=lambda x: x["puntaje"])
            mejor_id = mejor["cotizacion_id"]
            for cnd in candidatos:
                if cnd["cotizacion_id"] == mejor_id:
                    cnd["es_mejor"] = True

        adjudicacion_sugerida[i.id] = mejor_id
        por_item.append({
            "item_solicitud_id": i.id,
            "descripcion": getattr(i, "descripcion", ""),
            "tipo": getattr(i, "tipo", ""),
            "cantidad": cant.get(i.id, 1),
            "candidatos": candidatos,
            "mejor_cotizacion_id": mejor_id,
        })

    # ---- Ranking global corregido (usando valores convertidos) ----
    resultados = []
    for c in respondidas:
        lk = lookups[c.id]
        fin_scores, time_scores, gar_scores = [], [], []
        monedas_cotizadas = set()

        for i in items_solicitud:
            it = lk.get(i.id)
            moneda_cot = getattr(c, "moneda", "COP")

            # Financiero: 0 si no oferta el ítem
            if it and mejor_precio[i.id] > 0:
                precio_info = precios_por_item[i.id].get(c.id, {})
                precio_convertido = precio_info.get("precio_convertido", 0.0)
                if precio_convertido > 0:
                    fin_scores.append(mejor_precio[i.id] / precio_convertido * 100)
                else:
                    fin_scores.append(0.0)
                monedas_cotizadas.add(moneda_cot)
            else:
                fin_scores.append(0.0)

            # Tiempo: 0 si no oferta el ítem
            if it and it.tiempo_entrega_dias is not None:
                time_scores.append(_score_tiempo(it.tiempo_entrega_dias, menor_dias[i.id]))
            else:
                time_scores.append(0.0)

            # Garantía: 0 si no oferta el ítem o si no ofrece garantía
            if it:
                gar_scores.append(
                    _score_garantia(getattr(it, "garantia_meses", None), mayor_garantia[i.id])
                )
            else:
                gar_scores.append(0.0)

        s_fin = round(sum(fin_scores) / total_items, 1) if total_items else 0.0
        s_time = round(sum(time_scores) / total_items, 1) if total_items else 0.0
        s_gar = round(sum(gar_scores) / total_items, 1) if total_items else 0.0
        disp = len(lk)
        s_comp = round(disp / total_items * 100, 1) if total_items else 0.0
        s_cal = round(_num(getattr(c.proveedor, "calificacion", None)) * 10, 1) if c.proveedor else 0.0

        sub = {
            "financiero": s_fin,
            "tiempo_entrega": s_time,
            "garantia": s_gar,
            "completitud": s_comp,
            "calificacion": s_cal,
        }
        suma_pesos = sum(pesos.get(k, 0) for k in sub) or 1
        final = sum(sub[k] * pesos.get(k, 0) for k in sub) / suma_pesos

        # Total en valor convertido
        total_cot_convertido = 0.0
        moneda_cot_defecto = getattr(c, "moneda", "COP")

        for iid, it in lk.items():
            precio_original = _num(it.precio_unitario)
            precio_convertido = _obtener_precio_convertido(
                db, precio_original, moneda_cot_defecto, moneda_oportunidad
            )
            total_cot_convertido += precio_convertido * cant.get(iid, 1)

        resultados.append({
            "cotizacion_id": c.id,
            "proveedor_id": c.proveedor_id,
            "moneda_cotizacion": moneda_cot_defecto,
            "monedas_utilizadas": list(monedas_cotizadas),
            "total_convertido": round(total_cot_convertido, 2),
            "items_disponibles": disp,
            "items_totales": total_items,
            "calificacion": _num(getattr(c.proveedor, "calificacion", None)) if c.proveedor else 0.0,
            "subpuntajes": sub,
            "puntaje_final": round(final, 1),
            "es_ganador_sugerido": False,
        })

    ganador_id = None
    if resultados:
        mejor = max(resultados, key=lambda r: r["puntaje_final"])
        if mejor["puntaje_final"] > 0:
            ganador_id = mejor["cotizacion_id"]
            for r in resultados:
                if r["cotizacion_id"] == ganador_id:
                    r["es_ganador_sugerido"] = True

    return {
        "pesos": pesos,
        "moneda_oportunidad": moneda_oportunidad,
        "por_item": por_item,
        "adjudicacion_sugerida": adjudicacion_sugerida,
        "resultados": resultados,
        "ganador_sugerido_cotizacion_id": ganador_id,
    }
