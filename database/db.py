"""
Capa de acceso a datos (SQLite).

Contiene:
- Conexión a la base de datos.
- Creación del esquema (tablas) si no existen.
- Funciones de alto nivel usadas por la interfaz gráfica:
  usuarios, productos, clientes, ventas, caja y reportes.

Todo el sistema usa una sola base de datos SQLite ubicada en
data/pos_ferreteria.db (ver config.py). SQLite soporta múltiples
usuarios leyendo/escribiendo desde la misma máquina o red local
sin necesidad de instalar un servidor de base de datos aparte,
que es justo lo que necesita una ferretería pequeña.
"""

import sqlite3
import datetime
from contextlib import contextmanager

from config import DB_PATH
from utils.seguridad import hashear_password


# ---------------------------------------------------------------------
# CONEXIÓN
# ---------------------------------------------------------------------

def obtener_conexion() -> sqlite3.Connection:
    """
    Abre una conexión nueva a la base de datos.
    Cada operación abre y cierra su propia conexión para evitar
    problemas cuando varias pantallas usan la base al mismo tiempo.
    """
    conexion = sqlite3.connect(DB_PATH)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion


@contextmanager
def cursor_db():
    """
    Context manager cómodo:

        with cursor_db() as cur:
            cur.execute(...)

    Hace commit automático al salir si no hubo errores, y rollback
    si hubo una excepción. Cierra la conexión siempre.
    """
    conexion = obtener_conexion()
    try:
        cur = conexion.cursor()
        yield cur
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


# ---------------------------------------------------------------------
# ESQUEMA
# ---------------------------------------------------------------------

def inicializar_base_datos():
    """
    Crea todas las tablas si no existen todavía. Es seguro llamar
    esta función cada vez que arranca la app.
    """
    with cursor_db() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('admin', 'vendedor')),
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_creacion TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                categoria TEXT,
                precio_venta REAL NOT NULL,
                costo REAL NOT NULL DEFAULT 0,
                stock INTEGER NOT NULL DEFAULT 0,
                unidad TEXT NOT NULL DEFAULT 'unidad',
                activo INTEGER NOT NULL DEFAULT 1
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                direccion TEXT,
                limite_credito REAL NOT NULL DEFAULT 0,
                saldo_deuda REAL NOT NULL DEFAULT 0,
                fecha_registro TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                cliente_id INTEGER,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                forma_pago TEXT NOT NULL CHECK (forma_pago IN ('efectivo', 'fiado', 'tarjeta')),
                anulada INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                nombre_producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS abonos_deuda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS cierres_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                total_efectivo REAL NOT NULL,
                total_fiado REAL NOT NULL,
                total_tarjeta REAL NOT NULL,
                total_general REAL NOT NULL,
                cantidad_ventas INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

    sembrar_datos_ejemplo()


# ---------------------------------------------------------------------
# DATOS DE EJEMPLO (SEED)
# ---------------------------------------------------------------------

def _hay_datos():
    with cursor_db() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM usuarios")
        return cur.fetchone()["n"] > 0


def sembrar_datos_ejemplo():
    """
    Si la base está vacía (primera vez que se abre la app), la
    llena con datos de ejemplo de una ferretería ficticia llamada
    "Ferretería El Tornillo Feliz": usuarios, productos de
    tornillería/herramientas y clientes fiado.
    """
    if _hay_datos():
        return

    ahora = datetime.datetime.now().isoformat(timespec="seconds")

    with cursor_db() as cur:
        # --- Usuarios de demo ---
        usuarios_demo = [
            ("Administrador General", "admin", "admin123", "admin"),
            ("Juan Pérez (Vendedor)", "vendedor", "vendedor123", "vendedor"),
        ]
        for nombre, usuario, password, rol in usuarios_demo:
            cur.execute(
                """INSERT INTO usuarios
                   (nombre_completo, usuario, password_hash, rol, activo, fecha_creacion)
                   VALUES (?, ?, ?, ?, 1, ?)""",
                (nombre, usuario, hashear_password(password), rol, ahora),
            )

        # --- Productos de ejemplo: tornillería y ferretería ---
        productos_demo = [
            ("7501234560012", "Tornillo Phillips 1/4 x 1\"", "Tornillería", 0.15, 0.07, 500, "unidad"),
            ("7501234560029", "Tornillo Phillips 1/4 x 2\"", "Tornillería", 0.20, 0.10, 400, "unidad"),
            ("7501234560036", "Tuerca hexagonal 1/4\"", "Tornillería", 0.10, 0.04, 600, "unidad"),
            ("7501234560043", "Clavo de 2 pulgadas (kg)", "Clavos", 1.80, 1.10, 50, "kg"),
            ("7501234560050", "Clavo de 3 pulgadas (kg)", "Clavos", 1.95, 1.20, 45, "kg"),
            ("7501234560067", "Cinta métrica 5m", "Herramientas", 4.50, 2.80, 25, "unidad"),
            ("7501234560074", "Martillo de uña 16oz", "Herramientas", 9.90, 6.20, 15, "unidad"),
            ("7501234560081", "Destornillador Phillips #2", "Herramientas", 3.25, 1.90, 30, "unidad"),
            ("7501234560098", "Destornillador plano #2", "Herramientas", 3.25, 1.90, 30, "unidad"),
            ("7501234560104", "Candado 40mm", "Seguridad", 6.75, 4.10, 20, "unidad"),
            ("7501234560111", "Alambre galvanizado (kg)", "Ferretería general", 2.30, 1.50, 40, "kg"),
            ("7501234560128", "Silicón transparente 280ml", "Selladores", 3.80, 2.20, 35, "unidad"),
            ("7501234560135", "Cinta aislante negra", "Eléctrico", 1.20, 0.60, 60, "unidad"),
            ("7501234560142", "Foco LED 9W luz blanca", "Eléctrico", 2.90, 1.70, 50, "unidad"),
            ("7501234560159", "Guantes de cuero para trabajo", "Seguridad", 5.50, 3.10, 20, "par"),
            ("7501234560166", "Pintura anticorrosiva 1/4 gal", "Pinturas", 8.90, 5.60, 18, "unidad"),
            ("7501234560173", "Brocha 2 pulgadas", "Pinturas", 2.10, 1.10, 40, "unidad"),
            ("7501234560180", "Llave inglesa 8\"", "Herramientas", 7.40, 4.50, 12, "unidad"),
            ("7501234560197", "Cinta de teflón", "Plomería", 0.80, 0.35, 70, "unidad"),
            ("7501234560203", "Tubo PVC 1/2\" (metro)", "Plomería", 1.50, 0.90, 100, "metro"),
        ]
        for codigo, nombre, categoria, precio, costo, stock, unidad in productos_demo:
            cur.execute(
                """INSERT INTO productos
                   (codigo_barras, nombre, categoria, precio_venta, costo, stock, unidad, activo)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (codigo, nombre, categoria, precio, costo, stock, unidad),
            )

        # --- Clientes de ejemplo (algunos con deuda / fiado) ---
        clientes_demo = [
            ("Constructora Los Andes S.A.", "8888-1234", "Av. Central 100", 500.0, 120.50),
            ("Don Ramiro Gómez", "8888-5678", "Barrio San José, casa 12", 100.0, 35.00),
            ("Ferretería El Vecino (reventa)", "8888-9012", "Calle 5, local 3", 300.0, 0.0),
            ("María Fernanda López", "8888-3456", "Residencial Las Flores #22", 80.0, 15.75),
            ("Taller Mecánico El Rayo", "8888-7890", "Zona Industrial km 3", 250.0, 60.00),
        ]
        for nombre, telefono, direccion, limite, deuda in clientes_demo:
            cur.execute(
                """INSERT INTO clientes
                   (nombre, telefono, direccion, limite_credito, saldo_deuda, fecha_registro)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (nombre, telefono, direccion, limite, deuda, ahora),
            )


# ---------------------------------------------------------------------
# USUARIOS
# ---------------------------------------------------------------------

def autenticar_usuario(usuario: str, password: str):
    """
    Verifica usuario/contraseña. Devuelve el registro del usuario
    (dict-like sqlite3.Row) si es válido y está activo, o None.
    """
    from utils.seguridad import verificar_password

    with cursor_db() as cur:
        cur.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND activo = 1",
            (usuario,),
        )
        fila = cur.fetchone()

    if fila is None:
        return None
    if verificar_password(password, fila["password_hash"]):
        return fila
    return None


def listar_usuarios():
    with cursor_db() as cur:
        cur.execute("SELECT * FROM usuarios ORDER BY nombre_completo")
        return cur.fetchall()


def crear_usuario(nombre_completo, usuario, password, rol):
    ahora = datetime.datetime.now().isoformat(timespec="seconds")
    with cursor_db() as cur:
        cur.execute(
            """INSERT INTO usuarios
               (nombre_completo, usuario, password_hash, rol, activo, fecha_creacion)
               VALUES (?, ?, ?, ?, 1, ?)""",
            (nombre_completo, usuario, hashear_password(password), rol, ahora),
        )


def cambiar_estado_usuario(usuario_id: int, activo: bool):
    with cursor_db() as cur:
        cur.execute(
            "UPDATE usuarios SET activo = ? WHERE id = ?",
            (1 if activo else 0, usuario_id),
        )


def cambiar_password_usuario(usuario_id: int, nueva_password: str):
    with cursor_db() as cur:
        cur.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?",
            (hashear_password(nueva_password), usuario_id),
        )


# ---------------------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------------------

def buscar_producto_por_codigo(codigo_barras: str):
    with cursor_db() as cur:
        cur.execute(
            "SELECT * FROM productos WHERE codigo_barras = ? AND activo = 1",
            (codigo_barras.strip(),),
        )
        return cur.fetchone()


def buscar_productos_por_nombre(texto: str):
    with cursor_db() as cur:
        cur.execute(
            """SELECT * FROM productos
               WHERE activo = 1 AND nombre LIKE ?
               ORDER BY nombre""",
            (f"%{texto}%",),
        )
        return cur.fetchall()


def listar_productos():
    with cursor_db() as cur:
        cur.execute("SELECT * FROM productos WHERE activo = 1 ORDER BY nombre")
        return cur.fetchall()


def descontar_stock(producto_id: int, cantidad: int):
    with cursor_db() as cur:
        cur.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, producto_id),
        )


# ---------------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------------

def listar_clientes():
    with cursor_db() as cur:
        cur.execute("SELECT * FROM clientes ORDER BY nombre")
        return cur.fetchall()


def obtener_cliente(cliente_id: int):
    with cursor_db() as cur:
        cur.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        return cur.fetchone()


def crear_cliente(nombre, telefono, direccion, limite_credito):
    ahora = datetime.datetime.now().isoformat(timespec="seconds")
    with cursor_db() as cur:
        cur.execute(
            """INSERT INTO clientes
               (nombre, telefono, direccion, limite_credito, saldo_deuda, fecha_registro)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (nombre, telefono, direccion, limite_credito, ahora),
        )


def aumentar_deuda_cliente(cliente_id: int, monto: float):
    with cursor_db() as cur:
        cur.execute(
            "UPDATE clientes SET saldo_deuda = saldo_deuda + ? WHERE id = ?",
            (monto, cliente_id),
        )


def registrar_abono_deuda(cliente_id: int, usuario_id: int, monto: float):
    """Registra un abono (pago parcial o total) a la deuda de un cliente."""
    ahora = datetime.datetime.now().isoformat(timespec="seconds")
    with cursor_db() as cur:
        cur.execute(
            "UPDATE clientes SET saldo_deuda = MAX(0, saldo_deuda - ?) WHERE id = ?",
            (monto, cliente_id),
        )
        cur.execute(
            """INSERT INTO abonos_deuda (cliente_id, usuario_id, monto, fecha)
               VALUES (?, ?, ?, ?)""",
            (cliente_id, usuario_id, monto, ahora),
        )


# ---------------------------------------------------------------------
# VENTAS
# ---------------------------------------------------------------------

def registrar_venta(usuario_id: int, cliente_id, carrito: list, forma_pago: str):
    """
    Registra una venta completa de forma atómica (o todo se guarda,
    o nada, si algo falla en medio).

    carrito: lista de dicts con claves:
        producto_id, nombre, cantidad, precio_unitario, subtotal

    forma_pago: 'efectivo', 'tarjeta' o 'fiado'.

    Si es 'fiado', se requiere cliente_id y se incrementa su deuda.

    Devuelve el id de la venta creada.
    """
    ahora = datetime.datetime.now().isoformat(timespec="seconds")
    total = sum(item["subtotal"] for item in carrito)

    conexion = obtener_conexion()
    try:
        cur = conexion.cursor()
        cur.execute(
            """INSERT INTO ventas (usuario_id, cliente_id, fecha, total, forma_pago, anulada)
               VALUES (?, ?, ?, ?, ?, 0)""",
            (usuario_id, cliente_id, ahora, total, forma_pago),
        )
        venta_id = cur.lastrowid

        for item in carrito:
            cur.execute(
                """INSERT INTO detalle_ventas
                   (venta_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    venta_id,
                    item["producto_id"],
                    item["nombre"],
                    item["cantidad"],
                    item["precio_unitario"],
                    item["subtotal"],
                ),
            )
            cur.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (item["cantidad"], item["producto_id"]),
            )

        if forma_pago == "fiado" and cliente_id:
            cur.execute(
                "UPDATE clientes SET saldo_deuda = saldo_deuda + ? WHERE id = ?",
                (total, cliente_id),
            )

        conexion.commit()
        return venta_id
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def ventas_del_dia(fecha_iso: str = None):
    """Devuelve todas las ventas (no anuladas) de un día dado (YYYY-MM-DD)."""
    if fecha_iso is None:
        fecha_iso = datetime.date.today().isoformat()
    with cursor_db() as cur:
        cur.execute(
            """SELECT v.*, u.nombre_completo AS vendedor, c.nombre AS cliente
               FROM ventas v
               LEFT JOIN usuarios u ON u.id = v.usuario_id
               LEFT JOIN clientes c ON c.id = v.cliente_id
               WHERE v.fecha LIKE ? AND v.anulada = 0
               ORDER BY v.fecha DESC""",
            (f"{fecha_iso}%",),
        )
        return cur.fetchall()


# ---------------------------------------------------------------------
# CIERRE DE CAJA Y REPORTES
# ---------------------------------------------------------------------

def resumen_caja_del_dia(fecha_iso: str = None):
    """
    Calcula el resumen de caja del día: total en efectivo, total
    fiado, total tarjeta, total general y cantidad de ventas.
    """
    if fecha_iso is None:
        fecha_iso = datetime.date.today().isoformat()

    with cursor_db() as cur:
        cur.execute(
            """SELECT forma_pago, COALESCE(SUM(total), 0) AS total, COUNT(*) AS cantidad
               FROM ventas
               WHERE fecha LIKE ? AND anulada = 0
               GROUP BY forma_pago""",
            (f"{fecha_iso}%",),
        )
        filas = cur.fetchall()

    resumen = {
        "efectivo": 0.0, "fiado": 0.0, "tarjeta": 0.0,
        "cantidad_ventas": 0, "total_general": 0.0,
    }
    for fila in filas:
        resumen[fila["forma_pago"]] = fila["total"]
        resumen["cantidad_ventas"] += fila["cantidad"]
    resumen["total_general"] = resumen["efectivo"] + resumen["fiado"] + resumen["tarjeta"]
    return resumen


def guardar_cierre_caja(usuario_id: int):
    """Guarda una foto (snapshot) del cierre de caja del día actual."""
    resumen = resumen_caja_del_dia()
    ahora = datetime.datetime.now().isoformat(timespec="seconds")
    with cursor_db() as cur:
        cur.execute(
            """INSERT INTO cierres_caja
               (usuario_id, fecha, total_efectivo, total_fiado, total_tarjeta,
                total_general, cantidad_ventas)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                usuario_id, ahora, resumen["efectivo"], resumen["fiado"],
                resumen["tarjeta"], resumen["total_general"], resumen["cantidad_ventas"],
            ),
        )
    return resumen


def producto_mas_vendido_del_dia(fecha_iso: str = None):
    """Devuelve (nombre_producto, cantidad_total) del producto más vendido hoy, o None."""
    if fecha_iso is None:
        fecha_iso = datetime.date.today().isoformat()

    with cursor_db() as cur:
        cur.execute(
            """SELECT dv.nombre_producto, SUM(dv.cantidad) AS total_unidades
               FROM detalle_ventas dv
               JOIN ventas v ON v.id = dv.venta_id
               WHERE v.fecha LIKE ? AND v.anulada = 0
               GROUP BY dv.nombre_producto
               ORDER BY total_unidades DESC
               LIMIT 1""",
            (f"{fecha_iso}%",),
        )
        fila = cur.fetchone()
        return (fila["nombre_producto"], fila["total_unidades"]) if fila else None


def top_productos_del_dia(fecha_iso: str = None, limite: int = 5):
    if fecha_iso is None:
        fecha_iso = datetime.date.today().isoformat()
    with cursor_db() as cur:
        cur.execute(
            """SELECT dv.nombre_producto, SUM(dv.cantidad) AS total_unidades,
                      SUM(dv.subtotal) AS total_vendido
               FROM detalle_ventas dv
               JOIN ventas v ON v.id = dv.venta_id
               WHERE v.fecha LIKE ? AND v.anulada = 0
               GROUP BY dv.nombre_producto
               ORDER BY total_unidades DESC
               LIMIT ?""",
            (f"{fecha_iso}%", limite),
        )
        return cur.fetchall()


def clientes_con_deuda():
    with cursor_db() as cur:
        cur.execute(
            "SELECT * FROM clientes WHERE saldo_deuda > 0 ORDER BY saldo_deuda DESC"
        )
        return cur.fetchall()
