import os
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException, HTTPError#import nuevo

from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional

# ---------------- Configuración de Logging ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------- Cargar variables de entorno ----------------
def load_env_variables() -> Optional[Dict[str, str]]:
    load_dotenv()
    api_key = os.getenv('API_KEY_SEARCH_GOOGLE')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        logging.error("API Key o Search Engine ID no encontrados en el archivo .env")
        return None
    logging.info("API Key y Search Engine ID cargados correctamente.")
    return {
        'api_key': api_key,
        'search_engine_id': search_engine_id
    }

# ---------------- Realizar búsqueda en Google ----------------
def perform_google_search(api_key: str, search_engine_id: str, query: str, start: int = 1, lang: str = "lang_es") -> Optional[List[Dict]]:
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "start": start,
        "lr": lang
    }

    try:
        response = requests.get(base_url, params=params, timeout=15)
        #response.raise_for_status()  # Levanta HTTPError si la respuesta no es 200 | Se comenta para manejar manualmente los errores

        if response.status_code >= 400:
            error_data = None
            try:
                # Intentar obtener detalles del error desde la respuesta JSON de Google
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'No specific error message provided.')
                logging.error(f"Error HTTP {response.status_code} de la API: {error_message}")
                logging.error(f"Detalles completos del error API: {error_data}")
            except ValueError: # Si la respuesta de error no es JSON válido
                logging.error(f"Error HTTP {response.status_code} de la API. Respuesta no es JSON: {response.text}")
            return None 

        try:
            data = response.json()
            return data.get("items", []) # Es vacía si no hay resultados
        except ValueError as e: # Error al parsear JSON en respuesta exitosa 
            logging.error(f"Respuesta exitosa (200 OK) pero no se pudo parsear JSON: {e}")
            logging.error(f"Contenido recibido: {response.text}")
            return None 

        #data = response.json()
        #return data.get("items", [])

    except ConnectionError:
        logging.error("Error de conexión: no se pudo resolver el nombre del host o no hay red.")
    except Timeout:
        logging.error("La solicitud ha superado el tiempo de espera.")
    except RequestException as e:
        logging.error(f"Ocurrió un error en la solicitud HTTP: {e}")
    except ValueError as e:
        logging.error(f"Error al parsear la respuesta JSON: {e}")
    except Exception as e:
        logging.exception("Ocurrió un error inesperado")
    
    return None


# ---------------- Mostrar resultados ----------------
def display_results(results: List[Dict]) -> None:
    for result in results:
        print("------- Nuevo resultado -------")
        print(f"Título: {result.get('title')}")
        print(f"Descripción: {result.get('snippet')}")
        print(f"Enlace: {result.get('link')}")
        print("-------------------------------")
        
# ---------------- Ejecución Principal ----------------
def main():
    env_vars = load_env_variables()
    if not env_vars:
        return

    #Query entregada en clases    
    #query = 'filetype:sql "MySQL dump" (pass|password|passwd|pwd)'

    #Query para buscar posibles contraseñas dentro de archivos de Log en sitios .cl (No encontró resultados)
    #query = 'filetype:log "password" | "pwd" site:cl'

    #Query para ver información expuesta en archivos php de ipchile.cl (No encontró resultados)
    #query = 'site:ipchile.cl filetype:php inurl:phpinfo.php'

    #Query para ver si en uchile.cl hay rastros de Joomla!
    #query = 'site:uchile.cl inurl:/component/ | filetype:xml "Joomla!"'

    #Query para ver si en gob.cl hay rastros de WordPress
    query = 'site:gob.cl inurl:wp-content | inurl:wp-admin | "Powered by WordPress"'
    logging.info(f"Ejecutando búsqueda con query: '{query}'") # Para saber qué query se usa


    results = perform_google_search(env_vars['api_key'], env_vars['search_engine_id'], query)

    if results is None:
        # perform_Google Search devolvió None, significa que ocurrió un error y ya fue loggeado
        logging.error("La búsqueda no pudo completarse debido a un error (revisar logs anteriores).")
    elif not results: # results es una lista vacía []
        logging.info("Búsqueda completada: No se encontraron resultados para esta query.")
    else: # results es una lista con elementos
        logging.info(f"Búsqueda completada: Se encontraron {len(results)} resultado(s).")
        display_results(results)
    

if __name__ == "__main__":
    main()


