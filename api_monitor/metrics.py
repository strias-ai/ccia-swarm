import requests
import time

def get_url_status(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.status_code, response.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        return None, str(e)

def main():
    urls = [
        "https://www.example.com",
        "https://www.nonexistentwebsite.com",
        "https://www.anotherexample.com"
    ]

    with open("metrics.log", "w") as log_file:
        for url in urls