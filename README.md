# POS Ferretería PRO

Sistema de punto de venta **multiusuario** para ferreterías pequeñas y medianas, escrito en Python con interfaz gráfica (CustomTkinter) y base de datos SQLite. Es la versión PRO del punto de venta gratuito de un solo usuario que se regaló en el video de YouTube "Regalo el punto de venta en Python que le hice a una ferretería (GRATIS, con código)".

## ¿Qué trae la versión PRO que no trae la gratis?

- **Multiusuario con roles**: administrador y vendedor, cada uno con su propio usuario y contraseña (hasheada con bcrypt, nunca en texto plano).
- **Permisos por rol**: el vendedor solo ve Venta, Clientes/Fiado y Cierre de caja. Reportes y Gestión de usuarios son exclusivos del administrador.
- **Cliente fiado**: registro de deuda por cliente, abonos parciales, saldo en tiempo real.
- **Cierre de caja**: resumen de efectivo, tarjeta y fiado del día, con historial de cierres.
- **Reportes**: producto más vendido, top 5 de productos, ventas totales del día, clientes con deuda pendiente.
- **Respaldo en la nube**: copia automática/manual de la base de datos con rotación de las últimas 7 copias, lista para apuntar a una carpeta de Dropbox, OneDrive o Google Drive.

## Requisitos

- Python 3.10 o superior.
- Windows, macOS o Linux con interfaz gráfica (no funciona por SSH sin entorno gráfico).

## Instalación rápida

```bash
cd pos-ferreteria-pro
pip install -r requirements.txt
python main.py
```

La primera vez que se ejecuta, la aplicación crea automáticamente la base de datos en `data/pos_ferreteria.db` y la llena con datos de ejemplo de una ferretería ficticia ("Ferretería El Tornillo Feliz"): productos de tornillería, clavos, herramientas, pinturas, plomería y eléctrico, además de clientes de ejemplo (algunos con deuda fiado).

## Usuario y clave de demostración

| Usuario     | Contraseña    | Rol       |
|-------------|---------------|-----------|
| `admin`     | `admin123`    | Administrador (ve todo, incluyendo Reportes y Usuarios) |
| `vendedor`  | `vendedor123` | Vendedor (solo Venta, Clientes/Fiado y Cierre de caja) |

**Importante**: cambia estas contraseñas de demostración antes de usar el sistema con datos reales de tu negocio (Menú "Usuarios" → seleccionar usuario → "Restablecer contraseña", disponible solo para el admin).

## Estructura de carpetas

```
pos-ferreteria-pro/
├── main.py                    # Punto de entrada de la aplicación
├── config.py                  # Rutas, constantes y configuración de respaldo
├── requirements.txt
├── README.md
├── MANUAL_INSTALACION.md      # Manual paso a paso para el cliente final (no técnico)
├── data/                      # Se crea automáticamente
│   ├── pos_ferreteria.db      # Base de datos SQLite
│   └── respaldos_nube/        # Copias de respaldo con rotación (últimas 7)
├── database/
│   └── db.py                  # Esquema, datos de ejemplo y todas las consultas
├── backup/
│   └── backup_manager.py      # Lógica de respaldo con timestamp y rotación
├── utils/
│   └── seguridad.py           # Hash y verificación de contraseñas (bcrypt)
└── ui/
    ├── login_window.py        # Pantalla de inicio de sesión
    ├── main_window.py         # Ventana principal con menú lateral por rol
    ├── venta_view.py          # Pantalla de venta (código de barras + carrito)
    ├── clientes_view.py       # Clientes y cuentas por cobrar (fiado)
    ├── caja_view.py           # Cierre de caja del día
    ├── reportes_view.py       # Reportes (solo admin) + respaldo manual
    └── usuarios_view.py       # Gestión de usuarios (solo admin)
```

## Cómo funciona el lector de código de barras

El campo de "código de barras" en la pantalla de Venta es un cuadro de texto normal. Un lector de código de barras USB físico funciona exactamente como un teclado que escribe muy rápido y presiona Enter al final — por eso este mismo campo funciona tanto si el cajero teclea el código a mano como si usa una pistola lectora real, sin configuración adicional.

## Respaldo en la nube

Por defecto, los respaldos se guardan en `data/respaldos_nube/` dentro del propio proyecto. Para que el respaldo realmente "suba a la nube", cambia la ruta `BACKUP_DIR` en `config.py` para que apunte a una carpeta sincronizada por tu servicio de nube preferido, por ejemplo:

- **Dropbox**: `C:\Users\TU_USUARIO\Dropbox\RespaldosFerreteria`
- **OneDrive**: `C:\Users\TU_USUARIO\OneDrive\RespaldosFerreteria`
- **Google Drive** (con Google Drive para escritorio): `G:\Mi unidad\RespaldosFerreteria`

Una vez que `BACKUP_DIR` apunta a esa carpeta, cada respaldo que hagas (botón "Respaldar ahora" en Reportes) se sincroniza solo con la nube, porque la app de Dropbox/OneDrive/Drive vigila esa carpeta en segundo plano. Se conservan automáticamente las últimas 7 copias; las más antiguas se borran solas.

Ver `MANUAL_INSTALACION.md` para instrucciones detalladas paso a paso.

## Licencia de uso

Este código se entrega como parte de una recompensa de Patreon para uso del negocio del suscriptor. No está pensado para redistribución ni reventa como producto independiente.
