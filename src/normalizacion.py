"""Reglas de normalización de los datos de leads."""
import re
import unicodedata

from dateutil import parser as dateparser


def _sin_acentos(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def _clave(texto):
    t = _sin_acentos(str(texto).strip().lower()).replace(".", "")
    return re.sub(r"\s+", " ", t)


def limpiar_espacios(valor):
    """Recorta y colapsa espacios; None si queda vacío."""
    if valor is None:
        return None
    s = re.sub(r"\s+", " ", str(valor).strip())
    return s or None


def normalizar_telefono(valor):
    """Devuelve el teléfono en 10 dígitos; None si no es un número válido."""
    if valor is None:
        return None
    d = re.sub(r"\D", "", str(valor))
    if d.startswith("57") and len(d) == 12:
        d = d[2:]
    d = d.lstrip("0")
    if len(d) >= 10:
        return d[-10:]
    return None


def normalizar_email(valor):
    """Email en minúsculas; None si está vacío."""
    if not valor or not str(valor).strip():
        return None
    return str(valor).strip().lower()


def normalizar_nombre(valor):
    """Nombre sin espacios sobrantes, en formato Título."""
    limpio = limpiar_espacios(valor)
    return limpio.title() if limpio else None


_CIUDADES = {
    "bogota": "Bogotá", "bogota dc": "Bogotá", "medellin": "Medellín",
    "monteria": "Montería", "itagui": "Itagüí", "santa marta": "Santa Marta",
    "sta marta": "Santa Marta", "soledad": "Soledad", "soacha": "Soacha",
    "cartagena": "Cartagena", "rio negro": "Rionegro", "rionegro": "Rionegro",
    "bello": "Bello", "envigado": "Envigado", "barranquilla": "Barranquilla",
}


def normalizar_ciudad(valor):
    """Unifica variantes de ciudad a un nombre canónico."""
    if not valor or not str(valor).strip():
        return None
    return _CIUDADES.get(_clave(valor), str(valor).strip().title())


_CANALES = {
    "whatsapp": "WhatsApp", "meta ads": "Meta Ads", "formulario web": "Formulario Web",
}


def normalizar_canal(valor):
    """Unifica el canal a WhatsApp, Meta Ads o Formulario Web."""
    if not valor or not str(valor).strip():
        return None
    return _CANALES.get(_clave(valor))


_ESTADOS = {
    "contactado": "Contactado", "cotizacion enviada": "Cotización enviada",
    "descartado": "Descartado", "en proceso": "En proceso",
    "no contesta": "No contesta", "sin gestion": "Sin gestión",
}


def normalizar_estado(valor):
    """Unifica el estado de gestión; conserva el original si no lo reconoce."""
    if not valor or not str(valor).strip():
        return None
    return _ESTADOS.get(_clave(valor), str(valor).strip())


def normalizar_fecha(valor):
    """Parsea fechas de formatos mixtos a datetime; None si no es válida.

    Cuando el separador es / o -, decide el orden día/mes por el valor:
    un número mayor a 12 solo puede ser el día.
    """
    if valor is None:
        return None
    v = str(valor).strip()
    if not v:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}", v):
        try:
            return dateparser.parse(v)
        except (ValueError, OverflowError):
            return None
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})", v)
    if m:
        primero, segundo = int(m.group(1)), int(m.group(2))
        dia_primero = True if primero > 12 else (False if segundo > 12 else True)
        try:
            return dateparser.parse(v, dayfirst=dia_primero)
        except (ValueError, OverflowError):
            return None
    try:
        return dateparser.parse(v, dayfirst=True)
    except (ValueError, OverflowError):
        return None


def a_entero(valor):
    """Convierte a int; None si no es un número."""
    try:
        return int(str(valor).strip())
    except (ValueError, TypeError):
        return None


def si_no_a_bool(valor):
    """'SI' -> True; otro valor -> False; None si está vacío."""
    if valor is None or not str(valor).strip():
        return None
    return str(valor).strip().upper() == "SI"
