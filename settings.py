# settings.py
import configparser
from pathlib import Path

# 1. Definimos la ruta raíz (igual que en tu spritepane.py)
root = Path(__file__).parent

# 2. Instanciamos y leemos el archivo
config = configparser.ConfigParser()
# Usamos root para asegurar que siempre encuentre el archivo, 
# sin importar desde dónde se ejecute el script.
config.read(root / "config.ini", encoding="utf-8")

# 3. (Opcional) Validación básica: si no existe el archivo, avisamos
if not config.read(root / "config.ini"):
    print("Advertencia: No se encontró config.ini, usando valores por defecto.")