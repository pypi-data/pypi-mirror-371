from os import environ, sep
from pathlib import Path
from .errors import PathValidateError

base_path = environ.get('BASE_PATH', '')

def path_validator(pathstring: str) -> bool:
    path = Path(pathstring)

    if path.is_absolute():
        raise PathValidateError('La ruta especificada es incorrecta. No se aceptan rutas absolutas')
    path_parts = path.parts
    if '..' in path_parts:
        raise PathValidateError('La ruta especificada es incorrecta. Estás intentando salir del ambito')

    return True
