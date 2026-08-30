Aquí tienes el contenido del archivo `utils.py` basado en tus instrucciones:

```python
def install_package(package_name):
    try:
        import subprocess
        subprocess.run(['pip', 'install', package_name], check=True)
        print(f"El paquete {package_name} se ha instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar el paquete {package_name}: {e}")

def check_package(package_name):
    try:
        import pkg_resources
        if pkg_resources.find_distribution(package_name):
            print(f"El paquete {package_name} está instalado.")
        else:
            print(f"El paquete {package_name} no está instalado.")
    except pkg_resources.DistributionNotFound:
        print(f"El paquete {package_name} no está instalado.")

def update_package(package_name):
    try:
        import subprocess
        subprocess.run(['pip', 'install', '--upgrade', package_name], check=True)
        print(f"El paquete {package_name} se ha actualizado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al actualizar el paquete {package_name}: {e}")
```

Este archivo contiene tres funciones:

1. `install_package(package_name)`: Instala un paquete utilizando `pip`.
2. `check_package(package_name)`: Verifica si un paquete está instalado.
3. `update_package(package_name)`: Actualiza un paquete utilizando `pip`.