"""Transformación de datos: limpieza y normalización."""
import pandas as pd

from src import normalizacion as norm


def transformar_leads(df_crudo):
    """Normaliza los leads y devuelve las columnas de la tabla lead."""
    df = df_crudo
    return pd.DataFrame({
        "lead_id_origen": df["lead_id"],
        "empresa_id": df["empresa_id"],
        "punto_venta_id": df["punto_venta_id"],
        "canal": df["canal"].map(norm.normalizar_canal),
        "fecha_registro": df["fecha_registro"].map(norm.normalizar_fecha),
        "nombre": df["nombre_cliente"].map(norm.normalizar_nombre),
        "telefono": df["telefono"].map(norm.normalizar_telefono),
        "email": df["email"].map(norm.normalizar_email),
        "ciudad": df["ciudad"].map(norm.normalizar_ciudad),
        "modelo_interes": df["modelo_interes_texto"].map(norm.limpiar_espacios),
        "estado": df["estado_gestion"].map(norm.normalizar_estado),
        "fecha_primer_contacto": df["fecha_primer_contacto"].map(norm.normalizar_fecha),
        "campania": df["campania"].map(norm.limpiar_espacios),
    })


def transformar_asesores(df_crudo):
    """Normaliza los asesores y devuelve las columnas de la tabla asesor."""
    df = df_crudo
    return pd.DataFrame({
        "asesor_id_origen": df["asesor_id"],
        "nombre": df["nombre"].map(norm.normalizar_nombre),
        "punto_venta_id": df["punto_venta_id"],
        "empresa_id": df["empresa_id"],
        "capacidad_diaria": df["capacidad_diaria_leads"].map(norm.a_entero),
        "activo": df["activo"].map(norm.si_no_a_bool),
        "fecha_ingreso": df["fecha_ingreso"].map(norm.normalizar_fecha),
    })


def transformar_catalogo(df_crudo):
    """Normaliza el catalogo (una fila por moto) para la tabla catalogo_moto."""
    df = df_crudo
    return pd.DataFrame({
        "sku": df["sku"],
        "marca": df["marca"].map(norm.limpiar_espacios),
        "linea": df["linea"].map(norm.limpiar_espacios),
        "cilindraje": df["cilindraje"].map(norm.a_entero),
        "segmento": df["segmento"].map(norm.limpiar_espacios),
        "precio_lista": df["precio_lista"].map(norm.a_entero),
        "unidades_disponibles": df["unidades_disponibles"].map(norm.a_entero),
    })


def explotar_disponibilidad(df_crudo):
    """Explota la lista de puntos de venta en filas moto-punto de venta."""
    d = df_crudo[["sku", "puntos_venta_disponibles"]].copy()
    d["punto_venta_id"] = d["puntos_venta_disponibles"].str.split("|")
    d = d.explode("punto_venta_id")
    d["punto_venta_id"] = d["punto_venta_id"].str.strip()
    d = d[d["punto_venta_id"] != ""]
    return d[["sku", "punto_venta_id"]].reset_index(drop=True)


def transformar_historico(df_crudo):
    """Normaliza el historico de cierres para la tabla historico_cierre."""
    df = df_crudo
    return pd.DataFrame({
        "lead_id_origen": df["lead_id"],
        "fecha_registro": df["fecha_registro"].map(norm.normalizar_fecha),
        "canal": df["canal"].map(norm.normalizar_canal),
        "empresa_id": df["empresa_id"],
        "punto_venta_id": df["punto_venta_id"],
        "modelo_cotizado": df["modelo_cotizado"].map(norm.limpiar_espacios),
        "precio_lista": df["precio_lista"].map(norm.a_entero),
        "horas_primer_contacto": df["horas_al_primer_contacto"].map(norm.a_decimal),
        "numero_contactos": df["numero_contactos"].map(norm.a_entero),
        "manifesto_cuota_inicial": df["manifesto_cuota_inicial"].map(norm.limpiar_espacios),
        "forma_pago": df["forma_pago_declarada"].map(norm.limpiar_espacios),
        "pidio_cita": df["pidio_cita"].map(norm.si_no_a_bool),
        "desenlace": df["desenlace"].map(norm.limpiar_espacios),
    })


def _texto_conversacion(mensajes):
    lineas = []
    for m in mensajes or []:
        emisor = m.get("emisor", "")
        texto = m.get("texto", "")
        lineas.append(f"{emisor}: {texto}")
    return "\n".join(lineas)


def transformar_conversaciones(df_crudo):
    """Aplana cada conversación a una fila con el texto completo."""
    df = df_crudo
    return pd.DataFrame({
        "conversacion_id": df["conversacion_id"],
        "lead_id_origen": df["lead_id"],
        "canal": df["canal"].map(norm.normalizar_canal),
        "fecha_inicio": df["fecha_inicio"].map(norm.normalizar_fecha),
        "texto": df["mensajes"].map(_texto_conversacion),
    })
