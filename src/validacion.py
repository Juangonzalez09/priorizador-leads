"""Validación de calidad: descarta registros no utilizables."""


def validar_leads(df):
    """Devuelve solo los leads contactables (con teléfono o email)."""
    contactable = df["telefono"].notna() | df["email"].notna()
    return df[contactable].reset_index(drop=True)
