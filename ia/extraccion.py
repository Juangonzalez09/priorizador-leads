"""Extracción de datos de una conversación con Gemini."""
import json

from google import genai
from google.genai import types

from config.config import GEMINI_API_KEY, GEMINI_MODEL
from ia.esquema import ExtraccionLead

INSTRUCCION = (
    "Eres un analista comercial de una comercializadora de motos en Colombia. "
    "Recibes una conversación de WhatsApp entre un cliente y un asesor. Extrae la "
    "información según el esquema; si un dato no aparece, déjalo vacío y no inventes. "
    "forma_pago: contado, credito, mixto o desconocido. "
    "intencion: alta, media o baja."
)

_cliente = None


def _obtener_cliente():
    global _cliente
    if _cliente is None:
        _cliente = genai.Client(api_key=GEMINI_API_KEY)
    return _cliente


def extraer(texto):
    """Extrae los 8 campos de una conversación."""
    resp = _obtener_cliente().models.generate_content(
        model=GEMINI_MODEL,
        contents=texto,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCCION,
            response_mime_type="application/json",
            response_schema=ExtraccionLead,
        ),
    )
    if getattr(resp, "parsed", None) is not None:
        return resp.parsed
    return ExtraccionLead(**json.loads(resp.text))
