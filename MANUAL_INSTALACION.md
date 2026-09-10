# Manual de instalación y uso — POS Ferretería PRO

Este manual está escrito para el dueño o encargado de la ferretería, **sin conocimientos técnicos**. Sigue los pasos en orden y en menos de 15 minutos tendrás el sistema funcionando.

---

## 1. Qué necesitas antes de empezar

- Una computadora con Windows 10 u 11 (también funciona en Mac).
- Conexión a internet (solo para la instalación inicial).
- La carpeta `pos-ferreteria-pro` que te compartimos (por Patreon).

---

## 2. Instalar Python

Si tu computadora ya tiene Python instalado, puedes saltar al paso 3.

1. Entra a [python.org/downloads](https://www.python.org/downloads/).
2. Descarga la versión más reciente (botón amarillo grande).
3. Abre el instalador descargado.
4. **Muy importante**: en la primera pantalla del instalador, marca la casilla que dice **"Add Python to PATH"** (agregar Python al PATH) antes de hacer clic en "Install Now".
5. Espera a que termine la instalación y cierra el instalador.

---

## 3. Instalar el sistema

1. Copia la carpeta `pos-ferreteria-pro` a un lugar fijo de tu computadora, por ejemplo el Escritorio o `Documentos`.
2. Abre esa carpeta.
3. Haz clic derecho dentro de la carpeta (en un espacio vacío) y elige **"Abrir en Terminal"** o **"Abrir ventana de PowerShell aquí"** (el nombre varía según tu versión de Windows).
4. En la ventana negra/azul que se abre, escribe exactamente esto y presiona Enter:

   ```
   pip install -r requirements.txt
   ```

5. Espera a que termine de instalar (puede tardar 1-2 minutos). Verás varias líneas de texto — es normal.
6. Cuando termine, escribe:

   ```
   python main.py
   ```

   y presiona Enter.

7. Debería abrirse una ventana con el logo del sistema y los campos de "Usuario" y "Contraseña". ¡Listo, ya está instalado!

> **Consejo**: crea un acceso directo a este comando para no tener que repetir estos pasos cada vez. Pídele a la persona que te entregó el sistema que te ayude a crear un archivo `iniciar.bat` con el contenido `python main.py` dentro de la misma carpeta — así solo tendrás que hacer doble clic en ese archivo para abrir el sistema.

---

## 4. Primer inicio de sesión

El sistema viene con dos usuarios de ejemplo ya creados:

| Usuario     | Contraseña    | Para qué sirve |
|-------------|---------------|----------------|
| `admin`     | `admin123`    | Dueño / encargado — ve todo, incluyendo reportes y puede crear más usuarios |
| `vendedor`  | `vendedor123` | Empleado de mostrador — solo puede vender, atender fiados y cerrar caja |

1. Escribe `admin` en el campo Usuario y `admin123` en Contraseña.
2. Presiona "Ingresar".

### Cambia la contraseña de inmediato

Por seguridad, **no dejes la contraseña `admin123`** una vez que confirmes que todo funciona:

1. En el menú lateral, entra a **"Usuarios"**.
2. Selecciona el usuario `admin` en la tabla.
3. Haz clic en **"Restablecer contraseña"**.
4. Escribe una contraseña nueva y difícil de adivinar.

Haz lo mismo para el usuario `vendedor`, o crea un usuario nuevo con el nombre real de tu empleado (ver siguiente sección).

---

## 5. Crear un usuario para cada empleado

1. Inicia sesión como `admin`.
2. Ve a **"Usuarios"** en el menú lateral.
3. En el panel derecho, llena:
   - Nombre completo del empleado.
   - Usuario (con el que iniciará sesión, sin espacios, ej. `carlos`).
   - Contraseña.
   - Rol: elige `vendedor` para empleados de mostrador, o `admin` solo para quien deba ver reportes y dinero.
4. Haz clic en **"Crear usuario"**.

Si un empleado deja de trabajar en la ferretería, **no borres su usuario** (así se conserva el historial de sus ventas) — en su lugar, selecciónalo en la tabla y haz clic en **"Activar/Desactivar seleccionado"** para bloquearle el acceso.

---

## 6. Cómo hacer una venta

1. Con cualquier usuario (admin o vendedor), entra a **"Venta"** (es la pantalla que aparece al iniciar sesión).
2. Haz clic en el cuadro de texto grande que dice "Escanea o escribe el código de barras…".
3. Si tienes un lector de código de barras físico (pistola), simplemente escanea el producto — funciona automáticamente, como si fuera un teclado. Si no tienes lector, escribe el código a mano y presiona Enter.
4. El producto aparece en la lista de la izquierda (el carrito). Si escaneas el mismo producto varias veces, la cantidad sube sola.
5. Para corregir cantidades: selecciona el producto en la lista y usa los botones **"+1"**, **"-1"** o **"Quitar producto"**.
6. En el panel derecho, elige la **forma de pago**:
   - **Efectivo**: pago normal en billetes/monedas.
   - **Tarjeta**: pago con tarjeta de débito/crédito.
   - **Fiado**: el cliente se lleva la mercadería y paga después. Debes elegir el cliente en la lista desplegable (si no existe, créalo primero en "Clientes / Fiado").
7. Haz clic en **"Confirmar venta"** y confirma el mensaje que aparece.
8. La venta queda guardada, el inventario se descuenta automáticamente y el carrito se vacía listo para el siguiente cliente.

---

## 7. Cómo manejar clientes fiado

1. Ve a **"Clientes / Fiado"** en el menú lateral.
2. Para agregar un cliente nuevo: llena nombre, teléfono, dirección y un límite de crédito (el monto máximo que le permites deber), luego haz clic en **"Guardar cliente"**.
3. Cuando un cliente viene a **pagar (abonar) su deuda**:
   - Selecciónalo en la tabla de la izquierda.
   - Escribe el monto que está pagando en el campo "Monto a abonar".
   - Haz clic en **"Registrar abono"**.
   - El saldo de deuda del cliente baja automáticamente.

---

## 8. Cómo cerrar caja al final del día

1. Ve a **"Cierre de caja"** en el menú lateral.
2. Verás tarjetas con el total de Efectivo, Tarjeta, Fiado y el Total general del día, además de la lista completa de ventas.
3. Cuenta el dinero físico de la caja y compáralo con el total en "Efectivo" que muestra el sistema.
4. Haz clic en **"Hacer cierre de caja"** para guardar ese resumen en el historial permanente.

---

## 9. Reportes (solo para el administrador)

1. Inicia sesión como `admin`.
2. Ve a **"Reportes"** en el menú lateral (esta opción NO aparece si inicias sesión como vendedor — es intencional, para que los empleados no vean esta información).
3. Ahí verás: el producto más vendido del día, el top 5 de productos, el total vendido y la lista de clientes que todavía deben dinero.

---

## 10. Configurar el respaldo en la nube (muy importante)

Este sistema guarda toda tu información (ventas, clientes, deudas) en un solo archivo llamado `pos_ferreteria.db`, dentro de la carpeta `data`. Si esa computadora se daña o se pierde, **perderías toda la información del negocio** a menos que tengas un respaldo.

### Opción fácil: respaldo manual dentro de la misma carpeta

Por defecto, cada vez que haces clic en **"Respaldar ahora"** (pantalla de Reportes, solo admin), se guarda una copia con fecha y hora dentro de `data/respaldos_nube/`. El sistema guarda automáticamente solo las últimas 7 copias y borra las más viejas.

### Opción recomendada: respaldo automático a Dropbox, OneDrive o Google Drive

Para que el respaldo se suba solo a internet sin que tengas que hacer nada extra:

1. Instala en tu computadora la aplicación de escritorio de **Dropbox**, **OneDrive** (ya viene instalado en Windows 10/11) o **Google Drive**.
2. Anota la ruta de la carpeta que esa aplicación sincroniza, por ejemplo:
   - Dropbox: `C:\Users\TU_USUARIO\Dropbox`
   - OneDrive: `C:\Users\TU_USUARIO\OneDrive`
   - Google Drive: `G:\Mi unidad`
3. Dentro de esa carpeta, crea una subcarpeta nueva llamada, por ejemplo, `RespaldosFerreteria`.
4. Pide a la persona técnica que te entregó el sistema que abra el archivo `config.py` (dentro de la carpeta `pos-ferreteria-pro`) y cambie la línea:

   ```python
   BACKUP_DIR = os.path.join(BASE_DIR, "data", "respaldos_nube")
   ```

   por la ruta de tu carpeta sincronizada, por ejemplo:

   ```python
   BACKUP_DIR = r"C:\Users\TU_USUARIO\Dropbox\RespaldosFerreteria"
   ```

5. Guarda el archivo y reinicia el sistema.

Desde ese momento, cada vez que hagas clic en "Respaldar ahora", la copia se guardará directamente en esa carpeta y la aplicación de Dropbox/OneDrive/Google Drive la subirá a internet automáticamente, sin pasos adicionales.

**Recomendación**: haz un respaldo manual al final de cada día, justo después de cerrar caja.

---

## 11. Preguntas frecuentes

**¿Qué pasa si olvido mi contraseña?**
Pide a otro usuario administrador que entre a "Usuarios" y use "Restablecer contraseña" en tu usuario. Si solo existe un administrador y perdió su contraseña, contacta a la persona que te entregó el sistema.

**¿Puedo usar el sistema en dos computadoras al mismo tiempo?**
Esta versión guarda los datos en un archivo local (`pos_ferreteria.db`). Si quieres compartirlo entre dos computadoras al mismo tiempo, la forma más simple es colocar la carpeta `data` en una carpeta de red compartida o en la misma carpeta sincronizada de Dropbox/OneDrive que uses para respaldos (aunque para uso simultáneo intensivo se recomienda migrar a un servidor de base de datos — consulta con soporte).

**¿Cómo agrego productos nuevos?**
La versión actual precarga productos de ejemplo. Para agregar tus productos reales, pide soporte técnico para importar tu inventario, o solicita como mejora futura una pantalla de "Gestión de productos" dentro de la app.

---

¿Dudas o problemas? Contacta al soporte de Patreon donde obtuviste este sistema.
