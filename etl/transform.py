"""Transformación de datos: limpieza y normalización."""
import pandas as pd

from src import normalizacion as norm


def transformar_leads(df_crudo):
    """Normaliza los leads y devuelve las columnas de la tabla `lead`."""
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
    """Normaliza los asesores y devuelve las columnas de la tabla `asesor`."""
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
