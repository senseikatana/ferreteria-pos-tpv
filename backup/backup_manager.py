"""
Módulo de respaldo (backup) de la base de datos.

Copia el archivo SQLite a una carpeta configurable (BACKUP_DIR en
config.py) con un nombre que incluye fecha y hora, y mantiene
rotación: solo conserva las últimas N copias (BACKUP_MAX_COPIAS),
borrando automáticamente las más antiguas.

Cómo "sube a la nube": esta función solo copia un archivo a una
carpeta local. Si esa carpeta es en realidad la carpeta que
Dropbox, OneDrive o Google Drive sincronizan en la computadora,
el archivo se subirá solo, sin que este código necesite saber
nada de la nube. Ver README.md / MANUAL_INSTALACION.md para
instrucciones de cómo apuntar BACKUP_DIR a esa carpeta.
"""

import os
import shutil
import glob
import datetime

from config import DB_PATH, BACKUP_DIR, BACKUP_MAX_COPIAS

PREFIJO_RESPALDO = "pos_ferreteria_backup_"
EXTENSION_RESPALDO = ".db"


def hacer_respaldo(carpeta_destino: str = None) -> str:
    """
    Copia la base de datos actual a la carpeta de respaldo con un
    nombre único que incluye timestamp, y aplica rotación (borra
    las copias más antiguas si se supera BACKUP_MAX_COPIAS).

    Devuelve la ruta del archivo de respaldo recién creado.
    """
    destino = carpeta_destino or BACKUP_DIR
    os.makedirs(destino, exist_ok=True)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"No se encontró la base de datos en: {DB_PATH}. "
            "Abre la aplicación al menos una vez antes de respaldar."
        )

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"{PREFIJO_RESPALDO}{timestamp}{EXTENSION_RESPALDO}"
    ruta_destino = os.path.join(destino, nombre_archivo)

    # copy2 preserva metadatos (fecha de modificación, etc.)
    shutil.copy2(DB_PATH, ruta_destino)

    _rotar_respaldos(destino)

    return ruta_destino


def _rotar_respaldos(carpeta: str):
    """
    Mantiene solo las últimas BACKUP_MAX_COPIAS copias de respaldo
    en la carpeta indicada. Borra las más antiguas por fecha de
    modificación.
    """
    patron = os.path.join(carpeta, f"{PREFIJO_RESPALDO}*{EXTENSION_RESPALDO}")
    respaldos = sorted(glob.glob(patron), key=os.path.getmtime, reverse=True)

    respaldos_a_borrar = respaldos[BACKUP_MAX_COPIAS:]
    for archivo in respaldos_a_borrar:
        try:
            os.remove(archivo)
        except OSError:
            # Si un archivo está bloqueado/en uso, lo ignoramos y
            # seguimos con los demás en vez de romper el respaldo.
            pass


def listar_respaldos(carpeta_destino: str = None):
    """Devuelve la lista de respaldos existentes, más reciente primero."""
    destino = carpeta_destino or BACKUP_DIR
    patron = os.path.join(destino, f"{PREFIJO_RESPALDO}*{EXTENSION_RESPALDO}")
    respaldos = sorted(glob.glob(patron), key=os.path.getmtime, reverse=True)
    return respaldos


def restaurar_respaldo(ruta_respaldo: str):
    """
    Restaura la base de datos a partir de un archivo de respaldo.
    Hace primero un respaldo de seguridad de la base actual antes
    de sobrescribirla, por si algo sale mal.
    """
    if not os.path.exists(ruta_respaldo):
        raise FileNotFoundError(f"No existe el archivo de respaldo: {ruta_respaldo}")

    # Respaldo de seguridad de la base actual antes de restaurar
    if os.path.exists(DB_PATH):
        hacer_respaldo()

    shutil.copy2(ruta_respaldo, DB_PATH)
