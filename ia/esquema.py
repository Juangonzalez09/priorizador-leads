"""Campos que la IA extrae de una conversación."""
from typing import Optional

from pydantic import BaseModel


class ExtraccionLead(BaseModel):
    # Extracción directa de la conversación
    modelo_interes: Optional[str] = None
    presupuesto: Optional[str] = None
    cuota_inicial: Optional[str] = None
    forma_pago: Optional[str] = None
    intencion: Optional[str] = None
    objecion_principal: Optional[str] = None
    pidio_cita: bool = False
    pidio_cotizacion: bool = False
    
    # Enriquecimiento con catálogo (fuzzy matching)
    sku_identificado: Optional[str] = None
    marca: Optional[str] = None
    linea: Optional[str] = None
    precio_lista: Optional[int] = None
    cilindraje: Optional[int] = None
    similitud_sku: Optional[float] = None
