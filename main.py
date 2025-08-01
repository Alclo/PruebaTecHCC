import sys
import os
import multiprocessing
import time

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from services.geoloc_service import run_geoloc_service
from services.logic_service import run_logic_service

if __name__ == '__main__':
    proceso_geoloc = multiprocessing.Process(target=run_geoloc_service)
    proceso_logic = multiprocessing.Process(target=run_logic_service)
    

    proceso_geoloc.start()
    proceso_logic.start()
    
    print("\nAmbos servicios están en ejecución.")
    print("Puedes consultar la API de Lógica de Negocio en http://127.0.0.1:5002/hospital_mas_cercano")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servicios...")
        proceso_geoloc.terminate()
        proceso_logic.terminate()
        proceso_geoloc.join()
        proceso_logic.join()
        print("Servicios detenidos.")
