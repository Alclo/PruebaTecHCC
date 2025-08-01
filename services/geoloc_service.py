from flask import Flask, jsonify, request
from geopy.distance import great_circle

app = Flask(__name__)

@app.route('/calculate_destination', methods=['POST'])
def calculate_destination():
    data = request.json
    lat_inicial = data['lat']
    lon_inicial = data['lon']
    distancia_km = data['distancia_m'] / 1000

    latitud_destino = lat_inicial - (distancia_km / 111.1)
    coordenada_destino = (latitud_destino, lon_inicial)

    return jsonify({"lat": coordenada_destino[0], "lon": coordenada_destino[1]})

@app.route('/find_nearest', methods=['POST'])
def find_nearest():
    data = request.json
    origen = (data['origen']['lat'], data['origen']['lon'])
    puntos_a_comparar = data['puntos']
    
    punto_mas_cercano = None
    distancia_minima = float('inf')

    for punto in puntos_a_comparar:
        ubicacion_punto = (punto['lat'], punto['lon'])
        distancia = great_circle(origen, ubicacion_punto).kilometers
        if distancia < distancia_minima:
            distancia_minima = distancia
            punto_mas_cercano = punto['nombre']
            
    return jsonify({"punto_cercano": punto_mas_cercano, "distancia_km": distancia_minima})

def run_geoloc_service():
    print("Iniciando servicio de Geocalización en http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001)
