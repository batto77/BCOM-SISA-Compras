"""Servicio de conversión de monedas usando tasas de cambio."""
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.trm import TasaCambio


def obtener_tasa_cambio(db: Session, moneda: str) -> Decimal:
    """
    Obtiene la tasa de cambio vigente de una moneda a COP.

    Args:
        db: Sesión de BD
        moneda: Código de moneda (ej: USD, EUR, COP)

    Returns:
        Tasa de cambio (ej: 4200 para USD = 1 USD → 4200 COP)
        Si es COP, retorna 1.0
    """
    if moneda.upper() == "COP":
        return Decimal("1.0")

    tasa = db.query(TasaCambio).filter(
        TasaCambio.moneda == moneda.upper()
    ).first()

    if not tasa:
        raise ValueError(f"No hay tasa de cambio registrada para {moneda}")

    return tasa.tasa_cop


def convertir_a_cop(
    db: Session,
    monto: Decimal,
    moneda_origen: str
) -> Decimal:
    """
    Convierte un monto de una moneda a COP.

    Args:
        db: Sesión de BD
        monto: Monto a convertir
        moneda_origen: Moneda de origen (ej: USD, EUR, COP)

    Returns:
        Monto convertido a COP
    """
    if moneda_origen.upper() == "COP":
        return monto

    tasa = obtener_tasa_cambio(db, moneda_origen)
    return monto * tasa


def convertir_entre_monedas(
    db: Session,
    monto: Decimal,
    moneda_origen: str,
    moneda_destino: str
) -> Decimal:
    """
    Convierte un monto entre dos monedas.

    Args:
        db: Sesión de BD
        monto: Monto a convertir
        moneda_origen: Moneda de origen
        moneda_destino: Moneda de destino

    Returns:
        Monto convertido
    """
    if moneda_origen.upper() == moneda_destino.upper():
        return monto

    # Convertir a COP primero
    en_cop = convertir_a_cop(db, monto, moneda_origen)

    # Si destino es COP, listo
    if moneda_destino.upper() == "COP":
        return en_cop

    # Convertir de COP a destino
    tasa_destino = obtener_tasa_cambio(db, moneda_destino)
    return en_cop / tasa_destino
