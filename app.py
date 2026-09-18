"""Dashboard web: mis leads de hoy ordenados por prioridad.

Flask app simple, respeta separación por empresa (filtrar por empresa_id).
"""
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from db.conexion import Session
from db.modelos import Lead, Scoring, ExtraccionIA, Conversacion

app = Flask(__name__)

# Sin autenticación: la empresa se elige por parámetro (?empresa=EMP-02)
EMPRESA_DEFAULT = "EMP-01"


@app.route("/")
def index():
    """Vista principal: mis leads de hoy, filtrados por empresa."""
    empresa_actual = request.args.get("empresa", EMPRESA_DEFAULT)

    with Session() as s:
        empresas = [e[0] for e in s.query(Lead.empresa_id).distinct().order_by(Lead.empresa_id).all()]

        # Traer leads NO duplicados de la empresa, ordenados por score
        leads = s.query(
            Lead.lead_id_origen,
            Lead.nombre,
            Lead.telefono,
            Lead.email,
            Lead.ciudad,
            Lead.modelo_interes,
            Lead.canal,
            Lead.fecha_primer_contacto,
            Scoring.score,
            Scoring.temperatura,
            Scoring.razon_score,
            ExtraccionIA.intencion,
            ExtraccionIA.pidio_cita,
            ExtraccionIA.objecion_principal,
        ).filter(
            Lead.empresa_id == empresa_actual,
            (Lead.es_duplicado == False) | (Lead.es_duplicado.is_(None)),
        ).outerjoin(
            Scoring, Lead.lead_id_origen == Scoring.lead_id_origen
        ).outerjoin(
            ExtraccionIA, Lead.lead_id_origen == ExtraccionIA.lead_id_origen
        ).order_by(
            Scoring.score.desc().nulls_last(),
            Lead.fecha_registro.asc(),
        ).limit(100).all()
    
    # Formatear para template
    leads_data = []
    for lead in leads:
        leads_data.append({
            "lead_id": lead.lead_id_origen,
            "nombre": lead.nombre or "N/A",
            "telefono": lead.telefono or "N/A",
            "email": lead.email or "N/A",
            "ciudad": lead.ciudad or "N/A",
            "modelo_interes": lead.modelo_interes or "N/A",
            "canal": lead.canal,
            "score": lead.score or 0,
            "temperatura": lead.temperatura or "SIN_DATOS",
            "intencion": lead.intencion or "-",
            "pidio_cita": "Si" if lead.pidio_cita else "No",
            "objecion": lead.objecion_principal[:30] if lead.objecion_principal else "-",
            "razon": lead.razon_score or "Sin datos",
            "primer_contacto": lead.fecha_primer_contacto.strftime("%d-%m %H:%M") if lead.fecha_primer_contacto else "Nunca",
        })
    
    stats = {
        "total": len(leads_data),
        "urgentes": sum(1 for l in leads_data if l["temperatura"] == "URGENTE"),
        "medios": sum(1 for l in leads_data if l["temperatura"] == "MEDIA"),
        "bajos": sum(1 for l in leads_data if l["temperatura"] == "BAJA"),
        "sin_datos": sum(1 for l in leads_data if l["temperatura"] == "SIN_DATOS"),
        "empresa": empresa_actual,
    }

    return render_template(
        "index.html",
        leads=leads_data,
        stats=stats,
        now=datetime.now().strftime("%d-%m-%Y %H:%M"),
        empresas=empresas,
        empresa_actual=empresa_actual,
    )


@app.route("/api/lead/<lead_id>")
def api_lead(lead_id):
    """API: detalle de un lead (para futuras integraciones)."""
    with Session() as s:
        lead = s.query(Lead).filter(Lead.lead_id_origen == lead_id).first()
        if not lead:
            return jsonify({"error": "Not found"}), 404
        
        scoring = s.query(Scoring).filter(Scoring.lead_id_origen == lead_id).first()
        extraccion = s.query(ExtraccionIA).filter(ExtraccionIA.lead_id_origen == lead_id).first()
        conversacion = s.query(Conversacion).filter(Conversacion.lead_id_origen == lead_id).first()
        
        return jsonify({
            "lead": {
                "lead_id": lead.lead_id_origen,
                "nombre": lead.nombre,
                "telefono": lead.telefono,
                "email": lead.email,
                "ciudad": lead.ciudad,
                "canal": lead.canal,
            },
            "scoring": {
                "score": scoring.score if scoring else None,
                "temperatura": scoring.temperatura if scoring else None,
                "razon": scoring.razon_score if scoring else None,
            },
            "extraccion_ia": {
                "modelo": extraccion.modelo_interes if extraccion else None,
                "forma_pago": extraccion.forma_pago if extraccion else None,
                "intencion": extraccion.intencion if extraccion else None,
                "pidio_cita": extraccion.pidio_cita if extraccion else False,
                "objecion": extraccion.objecion_principal if extraccion else None,
            },
            "conversacion": {
                "existe": bool(conversacion),
            },
        })


@app.route("/api/stats")
def api_stats():
    """API: estadísticas generales."""
    empresa_actual = request.args.get("empresa", EMPRESA_DEFAULT)
    with Session() as s:
        total = s.query(Lead).filter(
            Lead.empresa_id == empresa_actual,
            (Lead.es_duplicado == False) | (Lead.es_duplicado.is_(None)),
        ).count()
        
        scoring_data = s.query(Scoring.temperatura).all()
        temps = [t[0] for t in scoring_data]
        
        return jsonify({
            "total_leads": total,
            "con_extraccion_ia": s.query(ExtraccionIA).count(),
            "temperaturas": {
                "URGENTE": temps.count("URGENTE"),
                "MEDIA": temps.count("MEDIA"),
                "BAJA": temps.count("BAJA"),
                "MUY_BAJA": temps.count("MUY_BAJA"),
            },
        })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
