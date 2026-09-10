"""
Configuración global del sistema POS Ferretería PRO.

Aquí se definen rutas, constantes y parámetros que la app usa
en distintos módulos. Si necesitas cambiar dónde se guarda la
base de datos o la carpeta de respaldos, este es el único
archivo que deberías tocar.
"""

import os

# Carpeta raíz del proyecto (donde vive este archivo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta de la base de datos SQLite
DB_PATH = os.path.join(BASE_DIR, "data", "pos_ferreteria.db")

# Carpeta de datos (se crea automáticamente si no existe)
DATA_DIR = os.path.join(BASE_DIR, "data")

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE RESPALDO EN LA NUBE
# ---------------------------------------------------------------------
# Por defecto respaldamos a una carpeta local dentro del proyecto
# (data/respaldos_nube). En un negocio real, esta ruta debe apuntar
# a una carpeta SINCRONIZADA por Dropbox, Google Drive o OneDrive,
# por ejemplo:
#
#   Windows + Dropbox:
#     C:\\Users\\TU_USUARIO\\Dropbox\\RespaldosFerreteria
#
#   Windows + OneDrive:
#     C:\\Users\\TU_USUARIO\\OneDrive\\RespaldosFerreteria
#
#   Windows + Google Drive (Streaming/Escritorio):
#     G:\\Mi unidad\\RespaldosFerreteria
#
# Con solo cambiar la carpeta que sincroniza esa app, el respaldo
# "sube a la nube" automáticamente sin que el negocio tenga que
# hacer nada más. Ver MANUAL_INSTALACION.md sección "Configurar
# respaldo en la nube".
BACKUP_DIR = os.path.join(BASE_DIR, "data", "respaldos_nube")

# Cuántas copias de respaldo mantener (rotación). Al superar este
# número se borra automáticamente la copia más antigua.
BACKUP_MAX_COPIAS = 7

# Nombre de la app (se usa en títulos de ventana, reportes, etc.)
NOMBRE_APP = "POS Ferretería PRO"
VERSION_APP = "1.0.0"

# Moneda para mostrar en pantalla (símbolo)
MONEDA = "$"

# Tema visual de CustomTkinter: "light", "dark" o "system"
TEMA = "dark"
COLOR_TEMA = "blue"  # blue, green, dark-blue

# Asegura que las carpetas necesarias existan al importar config
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
