"""Fuzzy matching para emparejar modelo_interes (texto libre) con catálogo (SKU)."""
from difflib import SequenceMatcher
from db.conexion import Session
from db.modelos import CatalogoMoto
from src.logger import obtener_logger

log = obtener_logger("fuzzy_matching")


def _similitud(a: str, b: str) -> float:
    """Calcula similitud entre dos strings (0-1)."""
    if not a or not b:
        return 0.0
    a = str(a).lower().strip()
    b = str(b).lower().strip()
    return SequenceMatcher(None, a, b).ratio()


def encontrar_sku(modelo_interes: str, umbral: float = 0.6) -> dict | None:
    """
    Busca el SKU más similar para un modelo de interés.
    
    Args:
        modelo_interes: Texto libre del modelo que busca el cliente
        umbral: Mínimo de similitud (0-1) para considerar un match
    
    Returns:
        Dict con {sku, marca, linea, precio_lista, cilindraje, similitud}
        o None si no hay match por encima del umbral
    """
    if not modelo_interes or not isinstance(modelo_interes, str):
        return None
    
    with Session() as s:
        catalogo = s.query(CatalogoMoto).all()
    
    if not catalogo:
        log.warning("Catálogo vacío, no se puede hacer fuzzy matching")
        return None
    
    mejores_matches = []
    
    for moto in catalogo:
        # Comparar contra diferentes campos del catálogo
        opciones = [
            f"{moto.marca} {moto.linea}",  # "Honda Navi"
            f"{moto.linea}",                # "Navi"
            f"{moto.marca}",                # "Honda"
        ]
        
        for opcion in opciones:
            sim = _similitud(modelo_interes, opcion)
            if sim >= umbral:
                mejores_matches.append({
                    "sku": moto.sku,
                    "marca": moto.marca,
                    "linea": moto.linea,
                    "precio_lista": moto.precio_lista,
                    "cilindraje": moto.cilindraje,
                    "segmento": moto.segmento,
                    "similitud": sim,
                })
    
    if not mejores_matches:
        return None
    
    # Retornar el de máxima similitud
    mejor = max(mejores_matches, key=lambda x: x["similitud"])
    return mejor
