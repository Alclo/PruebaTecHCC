import requests
from flask import Flask, jsonify
import time
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from geopy.exc import GeocoderTimedOut

app = Flask(__name__)

GEOLOC_SERVICE_URL = "http://127.0.0.1:5001"

geolocator = Nominatim(user_agent="my-app", timeout=10)

@app.route('/hospital_mas_cercano', methods=['GET'])
def encontrar_hospital():
    coordenadas_iniciales = {"lat": 19.392746, "lon": -99.172805}
    distancia_m = 200

    print("Calculando coordenadas del accidente...")
    try:
        respuesta_destino = requests.post(
            f"{GEOLOC_SERVICE_URL}/calculate_destination",
            json={"lat": coordenadas_iniciales['lat'], "lon": coordenadas_iniciales['lon'], "distancia_m": distancia_m}
        ).json()
        coordenadas_accidente = (respuesta_destino['lat'], respuesta_destino['lon'])
        print(f"Coordenadas del accidente calculadas: {coordenadas_accidente}")
    except requests.exceptions.ConnectionError as e:
        print(f"Error: No se pudo conectar al servicio de geolocalización. Asegúrate de que esté corriendo en el puerto 5001.")
        return jsonify({"error": "No se pudo conectar al servicio de geolocalización."}), 500

    hospitales_cerca = []
    try:
        print(f"Buscando con Nominatim (timeout de {geolocator.timeout} segundos)...")
        busqueda = f"hospital, {coordenadas_accidente[0]}, {coordenadas_accidente[1]}"
        locaciones = geolocator.geocode(busqueda, exactly_one=False, limit=10)
        
        if locaciones:
            print(f"Nominatim encontró {len(locaciones)} posibles ubicaciones.")
            for locacion in locaciones:
                distancia = great_circle(coordenadas_accidente, (locacion.latitude, locacion.longitude)).kilometers
                print(f"Ubicación encontrada: {locacion.address}, Distancia: {distancia:.2f} km")
                if distancia <= 5:
                    hospitales_cerca.append({
                        'nombre': locacion.address,
                        'lat': locacion.latitude,
                        'lon': locacion.longitude
                    })
        else:
            print("Nominatim no encontró ninguna ubicación para la búsqueda.")
    except GeocoderTimedOut as e:
        print(f"Error: La solicitud a Nominatim ha excedido el tiempo de espera. El servidor puede estar muy ocupado.")
        return jsonify({"distancia_km": float('inf'), "punto_cercano": None})
    except Exception as e:
        print(f"Error al buscar con Nominatim: {e}")
        return jsonify({"distancia_km": float('inf'), "punto_cercano": None})

    print(f"Se encontraron {len(hospitales_cerca)} hospitales dentro del radio de 5km.")
    
    respuesta_cercano = requests.post(
        f"{GEOLOC_SERVICE_URL}/find_nearest",
        json={"origen": {"lat": coordenadas_accidente[0], "lon": coordenadas_accidente[1]}, "puntos": hospitales_cerca}
    ).json()
    
    return jsonify(respuesta_cercano)

def run_logic_service():
    print("Iniciando servicio de Lógica de Negocio en http://127.0.0.1:5002")
    time.sleep(3) 
    app.run(host='0.0.0.0', port=5002)
