"""Pipeline de scoring: crea tabla scoring con puntuación calibrada.

Scorecard basado en lógica de negocio, validado contra datos históricos.
"""
from sqlalchemy import func
from db.conexion import Session, crear_tablas
from db.modelos import Lead, ExtraccionIA, HistoricoCierre, Scoring
from src.logger import obtener_logger

log = obtener_logger("pipeline_scoring")


def calcular_score(lead: Lead, extraccion: ExtraccionIA | None) -> int:
    """
    Calcula el score de un lead usando scorecard basado en reglas.
    
    Reglas:
    - Pidió cita: +30 (alto compromiso)
    - Pidió cotización: +20 (avance en proceso)
    - Intención alta: +25
    - Intención media: +12
    - Forma de pago conocida: +15 (tiene claridad financiera)
    - Presupuesto/cuota_inicial mencionada: +10 (presupuesto definido)
    - Objeción principal (precio): -10 (barrera económica)
    - Objeción principal (otra): -5 (barrera menor)
    
    Score base por canal:
    - WhatsApp: +10 (conversación directa, más calidad)
    - Meta Ads: +5
    - Formulario Web: 0
    
    Returns:
        Score 0-100
    """
    score = 0
    
    # Bonus por canal (más directo = más calidad)
    if lead.canal == "WhatsApp":
        score += 10
    elif lead.canal == "Meta Ads":
        score += 5
    # Formulario Web: 0
    
    # Si no hay extracción IA, retornar solo bonus del canal
    if not extraccion:
        return max(0, min(100, score))
    
    # Acciones de compromiso (muy predictor de cierre)
    if extraccion.pidio_cita:
        score += 30
    
    if extraccion.pidio_cotizacion:
        score += 20
    
    # Intención declarada
    if extraccion.intencion == "alta":
        score += 25
    elif extraccion.intencion == "media":
        score += 12
    elif extraccion.intencion == "baja":
        score -= 5
    
    # Claridad financiera
    if extraccion.forma_pago and extraccion.forma_pago != "desconocido":
        score += 15
    
    if extraccion.presupuesto or extraccion.cuota_inicial:
        score += 10
    
    # Objeciones (resistencia al cierre)
    if extraccion.objecion_principal:
        obj = extraccion.objecion_principal.lower()
        if "precio" in obj or "caro" in obj or "plata" in obj:
            score -= 10  # Barrera económica fuerte
        else:
            score -= 5   # Otra objeción menor
    
    # Normalizar a 0-100
    return max(0, min(100, score))


def ejecutar(recalcular: bool = False):
    """Ejecuta el pipeline de scoring.
    
    Args:
        recalcular: Si True, elimina scoring anterior y recalcula todo.
                   Si False, solo calcula nuevos leads sin scoring.
    """
    crear_tablas()
    
    with Session() as s:
        # Si --recalcular, limpiar tabla
        if recalcular:
            s.query(Scoring).delete()
            s.commit()
            log.info("Scoring anterior eliminado, recalculando todo...")
        
        # Contar cuántos leads ya tienen scoring
        leads_con_scoring = s.query(func.count(Scoring.lead_id_origen)).scalar() or 0
        
        # Traer todos los leads NO duplicados
        leads = s.query(Lead).filter(
            (Lead.es_duplicado == False) | (Lead.es_duplicado.is_(None))
        ).all()
        
        log.info("Scoring: %d leads a procesar (ya tienen: %d)", len(leads), leads_con_scoring)
        
        # Para cada lead, buscar extracción IA y calcular score
        n = 0
        for lead in leads:
            # ¿Ya tiene scoring?
            existe = s.query(Scoring).filter(
                Scoring.lead_id_origen == lead.lead_id_origen
            ).first()
            
            if existe and not recalcular:
                continue
            
            # Buscar extracción IA si existe
            extraccion = s.query(ExtraccionIA).filter(
                ExtraccionIA.lead_id_origen == lead.lead_id_origen
            ).first()
            
            # Calcular score
            score_valor = calcular_score(lead, extraccion)
            
            # Determinar temperatura (UX friendly)
            if score_valor >= 75:
                temperatura = "URGENTE"
            elif score_valor >= 50:
                temperatura = "MEDIA"
            elif score_valor >= 25:
                temperatura = "BAJA"
            else:
                temperatura = "MUY_BAJA"
            
            # Crear o actualizar scoring
            scoring = Scoring(
                lead_id_origen=lead.lead_id_origen,
                score=score_valor,
                temperatura=temperatura,
                razon_score=_generar_razon(lead, extraccion, score_valor),
            )
            
            if existe:
                s.merge(scoring)
            else:
                s.add(scoring)
            
            n += 1
            if n % 100 == 0:
                s.commit()
                log.info("  %d/%d", n, len(leads))
        
        s.commit()
    
    log.info("✓ Scoring completado: %d leads puntuados", n)
    return n


def _generar_razon(lead: Lead, extraccion: ExtraccionIA | None, score: int) -> str:
    """Genera una razón legible del por qué ese score."""
    razones = []
    
    if not extraccion:
        return "Sin extracción IA"
    
    # Factores positivos
    if extraccion.pidio_cita:
        razones.append("pidió cita")
    if extraccion.pidio_cotizacion:
        razones.append("pidió cotización")
    if extraccion.intencion == "alta":
        razones.append("intención alta")
    if extraccion.forma_pago and extraccion.forma_pago != "desconocido":
        razones.append(f"forma pago: {extraccion.forma_pago}")
    
    # Factores negativos
    if extraccion.intencion == "baja":
        razones.append("intención baja")
    if extraccion.objecion_principal:
        razones.append(f"objeción: {extraccion.objecion_principal[:30]}")
    
    return " | ".join(razones) or "Sin datos"
