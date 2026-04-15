from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Base de datos en memoria (Simulación)
inventory = []

@app.route('/')
def home():
    return render_template('index.html')

# --- ENDPOINTS REQUERIDOS ---

@app.route('/devices', methods=['GET']) # Obtener todos [cite: 12]
def get_devices():
    return jsonify(inventory), 200

@app.route('/devices/<id>', methods=['GET']) # Obtener uno [cite: 13]
def get_device(id):
    device = next((d for d in inventory if d['id'] == id), None)
    if not device:
        abort(404, description="Dispositivo no encontrado") # Manejo 404 [cite: 20]
    return jsonify(device), 200

@app.route('/devices', methods=['POST']) # Crear [cite: 14]
def create_device():
    data = request.json
    # Validación: campos no vacíos [cite: 19]
    required = ['nombre', 'tipo', 'estado', 'area']
    if not data or not all(k in data and str(data[k]).strip() for k in required):
        abort(400, description="Error: Campos obligatorios vacíos") # Manejo 400 [cite: 20]

    new_device = {
        "id": str(uuid.uuid4())[:8], # Generar IDs automáticamente [cite: 18, 33]
        "nombre": data['nombre'],
        "tipo": data['tipo'],
        "estado": data['estado'],
        "area": data['area'],
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    inventory.append(new_device)
    return jsonify(new_device), 201

@app.route('/devices/<id>', methods=['PUT']) # Actualizar [cite: 15]
def update_device(id):
    device = next((d for d in inventory if d['id'] == id), None)
    if not device:
        abort(404)
    data = request.json
    for key in ['nombre', 'tipo', 'estado', 'area']:
        if key in data:
            device[key] = data[key]
    return jsonify(device), 200

@app.route('/devices/<id>', methods=['DELETE']) # Eliminar [cite: 16]
def delete_device(id):
    global inventory
    inventory = [d for d in inventory if d['id'] != id]
    return jsonify({"mensaje": "Eliminado correctamente"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)