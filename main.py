from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)
CORS(app)

# Nombre del archivo que servirá como "Base de Datos"
DB_FILE = 'inventory.json'

# --- FUNCIONES DE AYUDA ---

def load_data():
    """Carga los datos desde el archivo JSON."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    """Guarda los datos en el archivo JSON."""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ENDPOINTS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def get_devices():
    inventory = load_data() # Leer del archivo
    return jsonify(inventory), 200

@app.route('/devices/<id>', methods=['GET'])
def get_device(id):
    inventory = load_data()
    device = next((d for d in inventory if d['id'] == id), None)
    if not device:
        abort(404, description="Dispositivo no encontrado")
    return jsonify(device), 200

@app.route('/devices', methods=['POST'])
def create_device():
    data = request.json
    required = ['nombre', 'tipo', 'estado', 'area']
    if not data or not all(k in data and str(data[k]).strip() for k in required):
        abort(400, description="Error: Campos obligatorios vacíos")

    inventory = load_data() # Cargar actuales
    new_device = {
        "id": str(uuid.uuid4())[:8],
        "nombre": data['nombre'],
        "tipo": data['tipo'],
        "estado": data['estado'],
        "area": data['area'],
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    inventory.append(new_device)
    save_data(inventory) # Guardar en el archivo
    return jsonify(new_device), 201

@app.route('/devices/<id>', methods=['PUT'])
def update_device(id):
    inventory = load_data()
    device = next((d for d in inventory if d['id'] == id), None)
    if not device:
        abort(404)
    
    data = request.json
    for key in ['nombre', 'tipo', 'estado', 'area']:
        if key in data:
            device[key] = data[key]
    
    save_data(inventory) # Guardar cambios
    return jsonify(device), 200

@app.route('/devices/<id>', methods=['DELETE'])
def delete_device(id):
    inventory = load_data()
    new_inventory = [d for d in inventory if d['id'] != id]
    save_data(new_inventory) # Guardar lista sin el eliminado
    return jsonify({"mensaje": "Eliminado correctamente"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)