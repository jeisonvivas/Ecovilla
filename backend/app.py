import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:921535@localhost:5432/proyect13')

engine = create_engine(DATABASE_URL, future=True)
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes available as Base.classes.<table_name>
try:
    Usuarios = Base.classes.usuarios
except AttributeError:
    Usuarios = None
try:
    Reciclaje = Base.classes.reciclaje
except AttributeError:
    Reciclaje = None
try:
    Bonificaciones = Base.classes.bonificaciones
except AttributeError:
    Bonificaciones = None

app = Flask(__name__)
CORS(app)

# Ajusta puntos por kg aquí
POINTS_PER_KG = {
    'plastico': 10,
    'plástico': 10,
    'vidrio': 5,
    'papel': 8,
    'metal': 12,
}

def compute_points(material:str, cantidad):
    if material is None:
        return 0
    m = material.strip().lower()
    pts_per = POINTS_PER_KG.get(m, 1)
    try:
        qty = float(cantidad)
    except:
        qty = 0
    return int(qty * pts_per)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status':'ok'})

@app.route('/usuarios', methods=['GET'])
def list_usuarios():
    if Usuarios is None:
        return jsonify({'error':'Tabla usuarios no encontrada en la DB.'}), 500
    with Session(engine) as session:
        rows = session.query(Usuarios).all()
        out = []
        for u in rows:
            out.append({c: getattr(u, c) for c in u.__table__.columns.keys()})
        return jsonify(out)

@app.route('/reciclaje', methods=['GET'])
def list_reciclaje():
    if Reciclaje is None:
        return jsonify({'error':'Tabla reciclaje no encontrada en la DB.'}), 500
    with Session(engine) as session:
        rows = session.query(Reciclaje).order_by(Reciclaje.id.desc()).limit(200).all()
        out = []
        for r in rows:
            out.append({c: getattr(r, c) for c in r.__table__.columns.keys()})
        return jsonify(out)

@app.route('/reciclaje', methods=['POST'])
def create_reciclaje():
    if Reciclaje is None:
        return jsonify({'error':'Tabla reciclaje no encontrada en la DB.'}), 500
    data = request.get_json() or {}
    usuarioid = data.get('usuarioid')
    material = data.get('material')
    cantidad = data.get('cantidad')
    fecha = data.get('fecha') or datetime.utcnow().isoformat()
    if usuarioid is None or material is None or cantidad is None:
        return jsonify({'error':'falta usuarioid, material o cantidad'}), 400
    points = compute_points(material, cantidad)
    # insert into reciclaje and into bonificaciones (if exists)
    with Session(engine) as session:
        # insert reciclaje
        new = Reciclaje()
        # set attributes dynamically for columns that exist
        cols = Reciclaje.__table__.columns.keys()
        if 'material' in cols: setattr(new, 'material', material)
        if 'cantidad' in cols: setattr(new, 'cantidad', cantidad)
        if 'fecha' in cols: setattr(new, 'fecha', fecha)
        if 'usuarioid' in cols: setattr(new, 'usuarioid', usuarioid)
        session.add(new)
        session.flush()  # ensure new.id available if needed
        # insert bonificaciones record if table exists
        if Bonificaciones is not None:
            # try to get user name
            nombre = None
            if Usuarios is not None:
                user = session.query(Usuarios).filter(getattr(Usuarios, 'id')==usuarioid).first()
                if user is not None:
                    nombre = getattr(user, 'nombre', None) or getattr(user, 'email', None)
            bon = Bonificaciones()
            bcols = Bonificaciones.__table__.columns.keys()
            if 'id_usuario' in bcols: setattr(bon, 'id_usuario', usuarioid)
            if 'nombre' in bcols: setattr(bon, 'nombre', nombre or '')
            if 'cantidad_bonificacion' in bcols: setattr(bon, 'cantidad_bonificacion', points)
            if 'fecha_entrega' in bcols: setattr(bon, 'fecha_entrega', datetime.utcnow().date())
            session.add(bon)
        session.commit()
    return jsonify({'ok':True, 'points': points})

@app.route('/ranking', methods=['GET'])
def ranking():
    # aggregate bonificaciones by id_usuario if table exists; otherwise fallback to users count
    if Bonificaciones is None:
        return jsonify({'error':'Tabla bonificaciones no encontrada, no hay ranking disponible.'}), 500
    with Session(engine) as session:
        # sum cantidad_bonificacion per id_usuario
        try:
            q = session.query(
                Bonificaciones.id_usuario.label('usuarioid'),
                func.sum(getattr(Bonificaciones, 'cantidad_bonificacion')).label('total')
            ).group_by(Bonificaciones.id_usuario).order_by(func.sum(getattr(Bonificaciones, 'cantidad_bonificacion')).desc())
        except Exception as e:
            return jsonify({'error':str(e)}), 500
        result = []
        for row in q.limit(50):
            usuarioid = row.usuarioid
            total = float(row.total or 0)
            name = None
            if Usuarios is not None:
                u = session.query(Usuarios).filter(getattr(Usuarios, 'id')==usuarioid).first()
                if u is not None:
                    name = getattr(u, 'nombre', None)
            result.append({'usuarioid': usuarioid, 'nombre': name, 'points': int(total)})
        return jsonify(result)

if __name__ == '__main__':
    print('Using DATABASE_URL =', DATABASE_URL)
    app.run(debug=True, host='0.0.0.0', port=5000)
