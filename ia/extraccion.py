"""Extracción de datos de una conversación con Gemini."""
import json

from google import genai
from google.genai import types

from config.config import GEMINI_API_KEY, GEMINI_MODEL
from ia.esquema import ExtraccionLead
from ia.fuzzy_matching import encontrar_sku
from src.logger import obtener_logger

log = obtener_logger("extraccion_ia")

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
    """Extrae los 8 campos de una conversación usando Chat con structured output.
    
    También enriquece con fuzzy matching del modelo_interes al catálogo.
    """
    client = _obtener_cliente()
    
    # Usar Chat.send_message con structured output (recomendado por Google)
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtraccionLead,
        ),
    )
    
    # Enviar instrucción + texto en el primer mensaje
    mensaje_completo = f"{INSTRUCCION}\n\n{texto}"
    resp = chat.send_message(mensaje_completo)
    
    if getattr(resp, "parsed", None) is not None:
        resultado = resp.parsed
    else:
        resultado = ExtraccionLead(**json.loads(resp.text))
    
    # Enriquecimiento: fuzzy matching del modelo_interes con catálogo
    if resultado.modelo_interes:
        try:
            match = encontrar_sku(resultado.modelo_interes, umbral=0.5)
            if match:
                resultado.sku_identificado = match["sku"]
                resultado.marca = match["marca"]
                resultado.linea = match["linea"]
                resultado.precio_lista = match["precio_lista"]
                resultado.cilindraje = match["cilindraje"]
                resultado.similitud_sku = match["similitud"]
                log.info(
                    "Fuzzy match: '%s' → %s (similitud: %.2f)",
                    resultado.modelo_interes,
                    match["sku"],
                    match["similitud"],
                )
        except Exception as e:
            log.warning("Error en fuzzy matching: %s", str(e)[:100])
    
    return resultado
