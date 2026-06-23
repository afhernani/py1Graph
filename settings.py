# settings.py
import configparser
from pathlib import Path

# 1. Definimos la ruta raíz (igual que en tu spritepane.py)
root = Path(__file__).parent
# 2. Definimos la ruta del archivo de configuración
config_file = root / "config.ini"
# 3. Instanciamos y leemos el archivo
config = configparser.ConfigParser()

# Leemos el archivo (si no existe, no pasa nada, no da error)
config.read(config_file, encoding="utf-8")

# Si no hay secciones (archivo no existe O archivo está vacío)
if not config.sections():
    print("config.ini no encontrado o vacío. Generando valores por defecto...")
    
    config['APP'] = {
        'debug': 'true',
        'log_level': 'DEBUG',
        'default_dir': str(root) 
    }
    config['CANVAS'] = {
        'grid_size': '10',
        'bg_color': 'yellow',
        'width': '400',
        'height': '300'
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)


def save_config():
    """Función para guardar cambios en el config.ini"""
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
