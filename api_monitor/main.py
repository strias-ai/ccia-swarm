Aquí tienes el contenido para `main.py` basado en tus especificaciones:

```python
import requests
import time
import json

def get_url_status(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.status_code, 'OK'
    except requests.exceptions.RequestException as e:
        return 500, str(e)

def get_url_latency(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        response.raise_for_status()
        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        return None