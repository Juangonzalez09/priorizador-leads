"""Campos que la IA extrae de una conversación."""
from typing import Optional

from pydantic import BaseModel


class ExtraccionLead(BaseModel):
    modelo_interes: Optional[str] = None
    presupuesto: Optional[str] = None
    cuota_inicial: Optional[str] = None
    forma_pago: Optional[str] = None
    intencion: Optional[str] = None
    objecion_principal: Optional[str] = None
    pidio_cita: bool = False
    pidio_cotizacion: bool = False
