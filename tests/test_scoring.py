"""Validación del scoring contra datos históricos.

Calcula métricas de precisión (AUC, lift, distribución de cierres).

Nota: El histórico son leads de meses anteriores, no los actuales.
Usamos para validar la LÓGICA del scorecard (¿los que cerraron tienen
características similares a lo que nuestras reglas premian?).
"""
import pandas as pd
from db.conexion import Session
from db.modelos import HistoricoCierre
from src.logger import obtener_logger

log = obtener_logger("validar_scoring")


def _calcular_score_historico(row) -> int:
    """Calcula score del scorecard para un registro histórico.
    
    (Mismo scorecard que pipeline_scoring pero sin acceso a BD)
    """
    score = 0
    
    # Bonus por canal
    if row["canal"] == "WhatsApp":
        score += 10
    elif row["canal"] == "Meta Ads":
        score += 5
    
    # Acciones de compromiso
    if row.get("pidio_cita"):
        score += 30
    
    if row.get("numero_contactos", 0) >= 2:
        score += 15  # Múltiples contactos = interés
    
    if row.get("manifesto_cuota_inicial"):
        score += 10
    
    if row.get("forma_pago") and row["forma_pago"] not in ["desconocido", None, ""]:
        score += 15
    
    # Penalización: tiempo al primer contacto
    horas_contacto = row.get("horas_primer_contacto")
    if horas_contacto is not None and horas_contacto > 24:
        score -= 10  # No se tocó en 24h
    
    return max(0, min(100, score))


def validar_scoring():
    """Analiza el histórico para validar que el scorecard es sensible."""
    
    with Session() as s:
        # Traer todos los cierres históricos
        historicos = s.query(HistoricoCierre).all()
    
    if not historicos:
        log.warning("No hay datos históricos")
        return
    
    # Convertir a dataframe
    data = []
    for h in historicos:
        score = _calcular_score_historico({
            "canal": h.canal,
            "pidio_cita": h.pidio_cita,
            "numero_contactos": h.numero_contactos,
            "manifesto_cuota_inicial": h.manifesto_cuota_inicial,
            "forma_pago": h.forma_pago,
            "horas_primer_contacto": h.horas_primer_contacto,
        })
        
        es_cerrado = 1 if h.desenlace == "Cerrado" else 0
        
        data.append({
            "score": score,
            "desenlace": h.desenlace,
            "es_cerrado": es_cerrado,
            "numero_contactos": h.numero_contactos or 0,
            "horas_contacto": h.horas_primer_contacto or 0,
        })
    
    df = pd.DataFrame(data)
    
    log.info("✓ Analizando %d leads históricos", len(df))
    
    # Estadísticas por desenlace
    print("\n" + "="*60)
    print("DISTRIBUCIÓN DE SCORES POR DESENLACE (Histórico)")
    print("="*60 + "\n")
    
    for desenlace in sorted(df["desenlace"].unique()):
        subset = df[df["desenlace"] == desenlace]["score"]
        print(f"{desenlace}:")
        print(f"  Media: {subset.mean():.1f}")
        print(f"  Mediana: {subset.median():.1f}")
        print(f"  Min-Max: {subset.min()}-{subset.max()}")
        print(f"  Cantidad: {len(subset)}")
        print()
    
    # Lift
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)
    cerrados_total = df["es_cerrado"].sum()
    
    print("="*60)
    print("LIFT: Ganancia al llamar en orden de prioridad")
    print("="*60 + "\n")
    
    for percentil in [10, 25, 50]:
        n_llamar = int(len(df) * percentil / 100)
        cerrados_en_top = df_sorted.head(n_llamar)["es_cerrado"].sum()
        tasa_en_top = cerrados_en_top / n_llamar * 100 if n_llamar > 0 else 0
        tasa_base = cerrados_total / len(df) * 100
        lift = tasa_en_top / tasa_base if tasa_base > 0 else 1
        
        print(f"Top {percentil:2d}% ({n_llamar:4d} leads):")
        print(f"  Tasa cierre: {tasa_en_top:.1f}% vs {tasa_base:.1f}% (base)")
        print(f"  Lift: {lift:.2f}x (se cierran {lift:.2f}x más que el promedio)")
        print()
    
    # Correlación
    from scipy.stats import spearmanr
    corr, pval = spearmanr(df["score"], df["es_cerrado"])
    
    print("="*60)
    print("CORRELACIÓN")
    print("="*60 + "\n")
    print(f"Score vs. Cierre (Spearman): {corr:.3f}")
    print(f"P-value: {pval:.6f} {'✓ SIGNIFICATIVO' if pval < 0.05 else '⚠ No significativo'}")
    print()
    
    # Tasa de cierre por rango de score
    print("="*60)
    print("TASA DE CIERRE POR RANGO DE SCORE")
    print("="*60 + "\n")
    
    for min_s, max_s in [(75, 100), (50, 74), (25, 49), (0, 24)]:
        subset = df[(df["score"] >= min_s) & (df["score"] <= max_s)]
        if len(subset) > 0:
            tasa = subset["es_cerrado"].mean() * 100
            print(f"Score {min_s:2d}-{max_s:2d}: {tasa:5.1f}% cierre ({len(subset):4d} leads)")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    validar_scoring()
    print("\n💡 Tip: También puedes ejecutar con: python -m tests.test_scoring")
