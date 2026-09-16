"""Deduplicación de leads."""
import pandas as pd

# Prioridad del canónico (menor = mejor).
_ORDEN_CANAL = {"WhatsApp": 0, "Meta Ads": 1, "Formulario Web": 2}
_ORDEN_ESTADO = {
    "Cotización enviada": 0,
    "En proceso": 1,
    "Contactado": 2,
    "No contesta": 3,
    "Sin gestión": 4,
    "Descartado": 5,
}


def deduplicar_leads(df):
    """Marca es_duplicado y lead_canonico_id por (teléfono, empresa)."""
    df = df.copy()
    df["_pc"] = df["canal"].map(_ORDEN_CANAL).fillna(9)
    df["_pe"] = df["estado"].map(_ORDEN_ESTADO).fillna(9)
    df["_pf"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
    df = df.sort_values(
        ["_pc", "_pe", "_pf"],
        ascending=[True, True, False],
        na_position="last",
    ).reset_index(drop=True)

    df["es_duplicado"] = False
    df["lead_canonico_id"] = df["lead_id_origen"]

    con_tel = df[df["telefono"].notna()]
    canonico = con_tel.groupby(["telefono", "empresa_id"])["lead_id_origen"].transform("first")
    duplicado = con_tel.duplicated(subset=["telefono", "empresa_id"], keep="first")
    df.loc[con_tel.index, "lead_canonico_id"] = canonico
    df.loc[con_tel.index, "es_duplicado"] = duplicado

    return df.drop(columns=["_pc", "_pe", "_pf"])
