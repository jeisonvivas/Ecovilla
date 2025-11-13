import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime

# URL de conexión a PostgreSQL local
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql+psycopg2://postgres:921535@localhost:5432/proyect13'
)

engine = create_engine(DATABASE_URL, future=True)
Base = automap_base()

# Reflejar las tablas existentes
Base.prepare(engine, reflect=True)

# Clases detectadas en tu base
try:
    Usuarios = Base.classes.usuarios
except:
    Usuarios = None
try:
    Reciclaje = Base.classes.reciclaje
except:
    Reciclaje = None
try:
    Bonificaciones = Base.classes.bonificaciones
except:
    Bonificaciones = None

app = Flask(__name__)
CORS(app)

# Puntos por kg
POINTS_PER_KG = {
    'plastico': 10,
    'plástico': 10,
    'vidrio': 5,
    'papel': 8,
    'metal': 12,
}

def compute_points(material: str, cantidad):
    if material is None:
        return 0
    m = material.strip().lower()
    pts_per = POINTS_PER_KG.get(m, 1)
    try:
        qty = float(cantidad)
    except:
        qty = 0
    return int(qty * pts_per)

@app.route('/status')
def status():
    return jsonify({"status": "ok"})

@app.route('/usuarios', methods=['GET'])
def list_usuarios():
    if Usuarios is None:
        return jsonify({'error': 'Tabla usuarios no encontrada'}), 500
    with Session(engine) as session:
        data = session.query(Usuarios).all()
        return jsonify([{c: getattr(u, c) for c in u.__table__.columns.keys()} for u in data])

@app.route('/reciclaje', methods=['GET'])
def list_reciclaje():
    if Reciclaje is None:
        return jsonify({'error': 'Tabla reciclaje no encontrada'}), 500
    with Session(engine) as session:
        rows = session.query(Reciclaje).order_by(Reciclaje.id.desc()).limit(200).all()
        return jsonify([{c: getattr(r, c) for c in r.__table__.columns.keys()} for r in rows])

@app.route('/reciclaje', methods=['POST'])
def create_reciclaje():
    if Reciclaje is None:
        return jsonify({'error': 'Tabla reciclaje no encontrada'}), 500

    data = request.get_json()
    usuarioid = data.get('usuarioid')
    material = data.get('material')
    cantidad = data.get('cantidad')
    fecha = data.get('fecha') or datetime.utcnow().isoformat()

    points = compute_points(material, cantidad)

    with Session(engine) as session:
        # Insertar reciclaje
        new = Reciclaje()
        if 'material' in Reciclaje.__table__.columns: new.material = material
        if 'cantidad' in Reciclaje.__table__.columns: new.cantidad = cantidad
        if 'fecha' in Reciclaje.__table__.columns: new.fecha = fecha
        if 'usuarioid' in Reciclaje.__table__.columns: new.usuarioid = usuarioid
        session.add(new)
        session.flush()

        # Registrar puntos
        if Bonificaciones is not None:
            bon = Bonificaciones()
            if 'id_usuario' in Bonificaciones.__table__.columns: bon.id_usuario = usuarioid
            if 'nombre' in Bonificaciones.__table__.columns:
                user = session.query(Usuarios).filter(Usuarios.id == usuarioid).first()
                bon.nombre = getattr(user, 'nombre', '') if user else ''
            if 'cantidad_bonificacion' in Bonificaciones.__table__.columns:
                bon.cantidad_bonificacion = points
            if 'fecha_entrega' in Bonificaciones.__table__.columns:
                bon.fecha_entrega = datetime.utcnow().date()
            session.add(bon)

        session.commit()

    return jsonify({"ok": True, "points": points})

@app.route('/ranking', methods=['GET'])
def ranking():
    if Bonificaciones is None:
        return jsonify({'error': 'Tabla bonificaciones no encontrada'}), 500

    with Session(engine) as session:
        q = session.query(
            Bonificaciones.id_usuario,
            func.sum(Bonificaciones.cantidad_bonificacion).label('total')
        ).group_by(Bonificaciones.id_usuario).order_by(func.sum(Bonificaciones.cantidad_bonificacion).desc())

        result = []
        for row in q:
            user = session.query(Usuarios).filter(Usuarios.id == row.id_usuario).first()
            result.append({
                "usuarioid": row.id_usuario,
                "nombre": getattr(user, 'nombre', None) if user else None,
                "points": int(row.total)
            })
        return jsonify(result)

if __name__ == "__main__":
    print("Backend corriendo en http://localhost:5000")
    app.run(debug=True)

