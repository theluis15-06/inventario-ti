from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
# Crea un archivo llamado 'inventory.db' en tu carpeta del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DE DATOS (TABLA) ---
class Device(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.String(20))

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# --- ENDPOINTS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def get_devices():
    # Consulta todos los registros de la tabla
    devices = Device.query.all()
    inventory = []
    for d in devices:
        inventory.append({
            "id": d.id,
            "nombre": d.nombre,
            "tipo": d.tipo,
            "estado": d.estado,
            "area": d.area,
            "fecha_registro": d.fecha_registro
        })
    return jsonify(inventory), 200

@app.route('/devices/<id>', methods=['GET'])
def get_device(id):
    device = Device.query.get(id)
    if not device:
        abort(404, description="Dispositivo no encontrado")
    return jsonify({
        "id": device.id,
        "nombre": device.nombre,
        "tipo": device.tipo,
        "estado": device.estado,
        "area": device.area,
        "fecha_registro": device.fecha_registro
    }), 200

@app.route('/devices', methods=['POST'])
def create_device():
    data = request.json
    required = ['nombre', 'tipo', 'estado', 'area']
    if not data or not all(k in data and str(data[k]).strip() for k in required):
        abort(400, description="Error: Campos obligatorios vacíos")

    new_device = Device(
        id=str(uuid.uuid4())[:8],
        nombre=data['nombre'],
        tipo=data['tipo'],
        estado=data['estado'],
        area=data['area'],
        fecha_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    db.session.add(new_device)
    db.session.commit() # Guarda en el archivo .db
    
    return jsonify({
        "id": new_device.id,
        "nombre": new_device.nombre,
        "mensaje": "Registrado en SQL"
    }), 201

@app.route('/devices/<id>', methods=['PUT'])
def update_device(id):
    device = Device.query.get(id)
    if not device:
        abort(404)
    
    data = request.json
    if 'nombre' in data: device.nombre = data['nombre']
    if 'tipo' in data: device.tipo = data['tipo']
    if 'estado' in data: device.estado = data['estado']
    if 'area' in data: device.area = data['area']
    
    db.session.commit() # Guarda los cambios
    return jsonify({"id": device.id, "mensaje": "Actualizado correctamente"}), 200

@app.route('/devices/<id>', methods=['DELETE'])
def delete_device(id):
    device = Device.query.get(id)
    if not device:
        abort(404)
    
    db.session.delete(device)
    db.session.commit() # Elimina de la base de datos
    return jsonify({"mensaje": "Eliminado de la base de datos"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)