import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import hashlib
import os

# --- CONFIGURACIÓN VISUAL GLOBAL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FerreteriaTPV(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ TPV FERRETERÍA PRO ⚡")
        self.geometry("1280x800")
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False))
        
        self.db_name = "ferreteria.db"
        self.init_db()
        
        self.usuario_actual = None # Guardará {'id': 1, 'nombre': 'Admin', 'rol': 'admin'}
        self.carrito = []
        self.total_actual = 0.0

        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        # Registramos todas las pantallas
        for F in (LoginScreen, MenuPrincipal, FrameCaja, FrameClientes, FrameVentas, FrameFiado, FrameCierre, FrameInventario):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Iniciar en Login
        self.show_frame("LoginScreen")

    def init_db(self):
        """Crea tablas y usuarios semilla (seed)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla Usuarios (NUEVA)
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                          (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT)''')
        
        # Tablas existentes
        cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                          (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL, stock INTEGER, google_id TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                          (id INTEGER PRIMARY KEY, nombre TEXT, telefono TEXT, direccion TEXT, google_id TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id INTEGER PRIMARY KEY, fecha TEXT, total REAL, tipo_pago TEXT, usuario_id INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS detalles_venta 
                          (id INTEGER PRIMARY KEY, venta_id INTEGER, producto TEXT, cantidad INTEGER, subtotal REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS fiados 
                          (id INTEGER PRIMARY KEY, cliente_id INTEGER, monto REAL, fecha TEXT, pagado INTEGER)''')
        
        # --- SEED DE USUARIOS (Contraseñas hasheadas por seguridad básica) ---
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # admin123 -> hash sha256
            admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
            vendedor_pass = hashlib.sha256("vendedor123".encode()).hexdigest()
            
            cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)", 
                           ("admin", admin_pass, "Administrador", "admin"))
            cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)", 
                           ("vendedor", vendedor_pass, "Empleado 1", "vendedor"))

        # --- MIGRACIONES SEGURAS ---
        try: cursor.execute("ALTER TABLE productos ADD COLUMN google_id TEXT")
        except: pass
        try: cursor.execute("ALTER TABLE fiados ADD COLUMN cliente_id INTEGER")
        except: pass
        try: cursor.execute("ALTER TABLE ventas ADD COLUMN usuario_id INTEGER")
        except: pass

        # Datos de ejemplo si está vacío
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            productos_ejemplo = [
                ("Martillo", 15.50, 50, None), ("Caja Tornillos 1/4", 8.00, 100, None),
                ("Taladro Percutor", 85.00, 10, None), ("Cemento 50kg", 12.00, 200, None),
                ("Pintura Blanca 4L", 25.00, 30, None), ("Cable 2x1.5 (metro)", 1.50, 500, None)
            ]
            cursor.executemany("INSERT INTO productos (nombre, precio, stock, google_id) VALUES (?, ?, ?, ?)", productos_ejemplo)
            
        cursor.execute("SELECT COUNT(*) FROM clientes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO clientes (nombre, telefono, direccion, google_id) VALUES (?, ?, ?, ?)", 
                           ("Consumidor Final", "N/A", "N/A", None))
        
        conn.commit()
        conn.close()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def run_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_estilos_tabla(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b",
                        font=("Arial", 22, "bold"), rowheight=70, borderwidth=0)
        style.map("Treeview", background=[('selected', '#FFD700')], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", background="#404040", foreground="white", font=("Arial", 24, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#404040')])

    def logout(self):
        self.usuario_actual = None
        self.show_frame("LoginScreen")

# =========================================================
# PANTALLA DE LOGIN (Estilo Youtuber Pro)
# =========================================================
class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Centrar todo en la pantalla
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Tarjeta central de login
        login_card = ctk.CTkFrame(self, width=500, height=600, corner_radius=20, fg_color="#2b2b2b")
        login_card.grid(row=0, column=0, padx=20, pady=20)
        login_card.grid_propagate(False) # Evita que la tarjeta se encoja
        login_card.grid_columnconfigure(0, weight=1)
        
        # Icono / Título
        ctk.CTkLabel(login_card, text="🔧", font=ctk.CTkFont(size=60)).pack(pady=(40, 10))
        ctk.CTkLabel(login_card, text="POS Ferretería PRO", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(login_card, text="Sistema de punto de venta", font=ctk.CTkFont(size=16), text_color="gray").pack(pady=(0, 40))
        
        # Campos
        self.entry_user = ctk.CTkEntry(login_card, width=350, height=60, font=ctk.CTkFont(size=24), placeholder_text="Usuario")
        self.entry_user.pack(pady=10)
        
        self.entry_pass = ctk.CTkEntry(login_card, width=350, height=60, font=ctk.CTkFont(size=24), placeholder_text="Contraseña", show="*")
        self.entry_pass.pack(pady=10)
        self.entry_pass.bind("<Return>", lambda e: self.login())
        
        # Botón Ingresar Gigante
        ctk.CTkButton(login_card, text="Ingresar", width=350, height=70, font=ctk.CTkFont(size=28, weight="bold"), 
                      fg_color="#1F6AA5", hover_color="#144870", command=self.login).pack(pady=40)
        
        # Ayuda visual (Seed)
        ctk.CTkLabel(login_card, text="Demo → admin / admin123\nvendedor / vendedor123", font=ctk.CTkFont(size=14), text_color="gray").pack(side="bottom", pady=20)

    def on_show(self):
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.entry_user.focus_set()

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not username or not password:
            return
            
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_data = self.controller.run_db_query(
            "SELECT id, nombre, rol FROM usuarios WHERE username=? AND password=?", 
            (username, pass_hash)
        ).fetchone()
        
        if user_data:
            self.controller.usuario_actual = {"id": user_data[0], "nombre": user_data[1], "rol": user_data[2]}
            self.controller.show_frame("MenuPrincipal")
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# =========================================================
# MENÚ PRINCIPAL (Con control de roles)
# =========================================================
class MenuPrincipal(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=50, pady=20)
        
        self.lbl_bienvenida = ctk.CTkLabel(self.header_frame, text="", font=ctk.CTkFont(size=30, weight="bold"))
        self.lbl_bienvenida.pack(side="left")
        
        ctk.CTkButton(self.header_frame, text="🚪 CERRAR SESIÓN", font=ctk.CTkFont(size=20, weight="bold"), 
                      height=50, width=200, fg_color="red", command=self.controller.logout).pack(side="right")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", padx=50, pady=10)
        self.btn_frame = btn_frame

    def on_show(self):
        # Limpiar botones anteriores
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
            
        user = self.controller.usuario_actual
        self.lbl_bienvenida.configure(text=f"👤 Bienvenido, {user['nombre']} ({user['rol'].upper()})")

        # Definir botones según el rol
        botones = [
            ("1. CAJA / VENDER (F1)", "FrameCaja", "green", "all"),
            ("2. CLIENTES / CRM (F2)", "FrameClientes", "#1ABC9C", "admin"),
            ("3. HISTORIAL VENTAS (F3)", "FrameVentas", "blue", "all"),
            ("4. FIADOS (F4)", "FrameFiado", "orange", "all"),
            ("5. CIERRE DE CAJA (F5)", "FrameCierre", "red", "admin"),
            ("6. INVENTARIO (F8)", "FrameInventario", "#8E44AD", "admin"),
        ]

        row_idx = 0
        for texto, frame, color, rol_req in botones:
            if rol_req == "all" or user['rol'] == rol_req:
                btn = ctk.CTkButton(
                    self.btn_frame, text=texto, font=ctk.CTkFont(size=32, weight="bold"), height=80,
                    fg_color=color, hover_color="white", text_color_disabled="black",
                    command=lambda f=frame: self.navegar(f)
                )
                btn.grid(row=row_idx, column=0, pady=10, padx=50, sticky="ew")
                
                # Atajos dinámicos
                if "F1" in texto: self.controller.bind("<F1>", lambda e: self.navegar("FrameCaja"))
                if "F2" in texto and user['rol'] == 'admin': self.controller.bind("<F2>", lambda e: self.navegar("FrameClientes"))
                if "F3" in texto: self.controller.bind("<F3>", lambda e: self.navegar("FrameVentas"))
                if "F4" in texto: self.controller.bind("<F4>", lambda e: self.navegar("FrameFiado"))
                if "F5" in texto and user['rol'] == 'admin': self.controller.bind("<F5>", lambda e: self.navegar("FrameCierre"))
                if "F8" in texto and user['rol'] == 'admin': self.controller.bind("<F8>", lambda e: self.navegar("FrameInventario"))
                
                row_idx += 1

        self.btn_frame.columnconfigure(0, weight=1)

    def navegar(self, frame):
        self.controller.show_frame(frame)

# =========================================================
# MÓDULO DE CAJA (Diseño Táctil Vertical Corregido)
# =========================================================
class FrameCaja(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- IZQUIERDA: PRODUCTOS ---
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(left_frame, text="👇 TOCA UN PRODUCTO PARA AGREGAR 👇", font=ctk.CTkFont(size=28, weight="bold"), text_color="#00FF00").pack(pady=(0, 10))
        
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        self.entry_buscar = ctk.CTkEntry(search_frame, font=ctk.CTkFont(size=30), height=70, placeholder_text="🔍 Buscar producto aquí...")
        self.entry_buscar.pack(fill="x", ipadx=10)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_producto)

        self.tree_productos = ttk.Treeview(left_frame, columns=("Nombre", "Precio", "Stock"), show="headings")
        self.tree_productos.heading("Nombre", text="PRODUCTO")
        self.tree_productos.heading("Precio", text="PRECIO $")
        self.tree_productos.heading("Stock", text="STOCK")
        self.tree_productos.column("Nombre", width=400, stretch=True)
        self.tree_productos.column("Precio", width=150, anchor="center")
        self.tree_productos.column("Stock", width=150, anchor="center")
        self.tree_productos.pack(fill="both", expand=True)
        
        self.tree_productos.bind("<Button-1>", self.agregar_al_carrito)

        # --- DERECHA: TICKET Y BOTONES EN COLUMNA ---
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        ctk.CTkLabel(right_frame, text="🛒 TICKET ACTUAL", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(10, 5))

        self.tree_carrito = ttk.Treeview(right_frame, columns=("Prod", "Cant", "Subtotal"), show="headings", height=8)
        self.tree_carrito.heading("Prod", text="Producto")
        self.tree_carrito.heading("Cant", text="Cant")
        self.tree_carrito.heading("Subtotal", text="Total")
        self.tree_carrito.column("Prod", width=200, stretch=True)
        self.tree_carrito.column("Cant", width=50, anchor="center")
        self.tree_carrito.column("Subtotal", width=100, anchor="center")
        self.tree_carrito.pack(fill="both", expand=True, padx=10)
        
        self.lbl_total = ctk.CTkLabel(right_frame, text="TOTAL: $0.00", font=ctk.CTkFont(size=55, weight="bold"), text_color="yellow")
        self.lbl_total.pack(pady=15)

        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkButton(row1, text="💵 COBRAR EFECTIVO (F9)", font=ctk.CTkFont(size=26, weight="bold"), height=80, fg_color="green", command=lambda: self.cobrar("Efectivo")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(row1, text="💳 COBRAR TARJETA (F10)", font=ctk.CTkFont(size=26, weight="bold"), height=80, fg_color="blue", command=lambda: self.cobrar("Tarjeta")).pack(side="left", expand=True, fill="x", padx=(5, 0))

        ctk.CTkButton(btn_frame, text="📖 FIAR A CLIENTE (F11)", font=ctk.CTkFont(size=28, weight="bold"), height=80, fg_color="orange", command=self.fiar).pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="❌ BORRAR DEL TICKET (Supr)", font=ctk.CTkFont(size=24, weight="bold"), height=70, fg_color="red", command=self.borrar_del_carrito).pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="🏠 VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=24, weight="bold"), height=70, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(fill="x", pady=5)

        self.controller.bind("<F9>", lambda e: self.cobrar("Efectivo") if self.winfo_ismapped() else None)
        self.controller.bind("<F10>", lambda e: self.cobrar("Tarjeta") if self.winfo_ismapped() else None)
        self.controller.bind("<F11>", lambda e: self.fiar() if self.winfo_ismapped() else None)
        self.controller.bind("<Delete>", lambda e: self.borrar_del_carrito() if self.winfo_ismapped() else None)

    def on_show(self):
        self.actualizar_productos()
        self.carrito = []
        self.actualizar_carrito_ui()

    def buscar_producto(self, event=None):
        self.actualizar_productos(self.entry_buscar.get())

    def actualizar_productos(self, filtro=""):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        query = "SELECT nombre, precio, stock FROM productos WHERE nombre LIKE ? ORDER BY nombre ASC"
        rows = self.controller.run_db_query(query, (f"%{filtro}%",))
        for row in rows:
            self.tree_productos.insert("", "end", values=row)

    def agregar_al_carrito(self, event):
        region = self.tree_productos.identify("region", event.x, event.y)
        if region != "cell": return
        item_id = self.tree_productos.identify_row(event.y)
        if not item_id: return
        
        self.tree_productos.selection_set(item_id)
        selected = self.tree_productos.selection()
        if not selected: return
        
        values = self.tree_productos.item(selected[0])['values']
        nombre, precio, stock = values
        
        prod_data = self.controller.run_db_query("SELECT id FROM productos WHERE nombre=? AND precio=?", (nombre, precio)).fetchone()
        if not prod_data: return
        self._agregar_item((prod_data[0], nombre, precio, stock))

    def _agregar_item(self, item):
        prod_id, nombre, precio, stock = item
        if stock <= 0:
            messagebox.showwarning("Sin Stock", f"¡Cuidado! No hay existencia de {nombre}")
            return
        
        encontrado = False
        for i in self.carrito:
            if i[0] == prod_id:
                i[2] += 1
                i[4] = round(i[2] * float(precio), 2)
                encontrado = True
                break
        
        if not encontrado:
            self.carrito.append([prod_id, nombre, 1, float(precio), round(float(precio), 2)])
        self.actualizar_carrito_ui()

    def borrar_del_carrito(self):
        selected = self.tree_carrito.selection()
        if selected:
            index = self.tree_carrito.index(selected[0])
            if 0 <= index < len(self.carrito):
                self.carrito.pop(index)
        elif self.carrito:
            self.carrito.pop()
        self.actualizar_carrito_ui()

    def actualizar_carrito_ui(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        total = 0
        for item in self.carrito:
            self.tree_carrito.insert("", "end", values=(item[1], item[2], f"${item[4]:.2f}"))
            total += item[4]
        self.lbl_total.configure(text=f"TOTAL: ${total:.2f}")
        self.total_actual = total

    def cobrar(self, metodo):
        if not self.carrito: return
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = self.controller.usuario_actual['id']
        
        self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago, usuario_id) VALUES (?, ?, ?, ?)", (fecha, self.total_actual, metodo, user_id))
        venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]

        for item in self.carrito:
            self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)", (venta_id, item[1], item[2], item[4]))
            self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

        messagebox.showinfo("¡Venta Exitosa!", f"Cobrado: ${self.total_actual:.2f}\nMétodo: {metodo}")
        self.carrito = []
        self.actualizar_carrito_ui()
        self.actualizar_productos()
        self.entry_buscar.delete(0, "end")

    def fiar(self):
        if not self.carrito: return
        
        rows = self.controller.run_db_query("SELECT id, nombre FROM clientes ORDER BY nombre ASC").fetchall()
        if not rows:
            messagebox.showerror("Error", "No hay clientes. Pide al Admin que agregue uno.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Fiado")
        dialog.geometry("500x600")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="¿A QUIÉN LE FIAMOS?", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)
        listbox = tk.Listbox(dialog, font=("Arial", 24), height=12, bg="#2b2b2b", fg="white", selectbackground="#FFD700", selectforeground="black")
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        client_ids = []
        for row in rows:
            client_ids.append(row[0])
            listbox.insert(tk.END, f"{row[1]}")

        def confirmar_fiado():
            selection = listbox.curselection()
            if not selection: return
            
            cliente_id = client_ids[selection[0]]
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = self.controller.usuario_actual['id']
            
            self.controller.run_db_query("INSERT INTO fiados (cliente_id, monto, fecha, pagado) VALUES (?, ?, ?, ?)", (cliente_id, self.total_actual, fecha, 0))
            self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago, usuario_id) VALUES (?, ?, ?, ?)", (fecha, self.total_actual, "Fiado", user_id))
            venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]
            
            for item in self.carrito:
                self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)", (venta_id, item[1], item[2], item[4]))
                self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

            messagebox.showinfo("Fiado OK", f"Deuda de ${self.total_actual:.2f} registrada.", parent=dialog)
            self.carrito = []
            self.actualizar_carrito_ui()
            self.actualizar_productos()
            self.entry_buscar.delete(0, "end")
            dialog.destroy()

        ctk.CTkButton(dialog, text="✅ CONFIRMAR FIADO", font=ctk.CTkFont(size=30, weight="bold"), height=90, fg_color="orange", command=confirmar_fiado).pack(pady=20, padx=20, fill="x")

# =========================================================
# RESTO DE MÓDULOS (CRM, Inventario, Ventas, Fiados, Cierre)
# =========================================================
class FrameClientes(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()
        ctk.CTkLabel(self, text="👥 GESTIÓN DE CLIENTES (CRM)", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        form_frame.pack(padx=20, pady=10, fill="x")
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(row1, text="Nombre:", font=ctk.CTkFont(size=25)).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, font=ctk.CTkFont(size=30), height=60, placeholder_text="Ej: Constructora Pérez")
        self.entry_nombre.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(row1, text="Teléfono:", font=ctk.CTkFont(size=25)).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row1, font=ctk.CTkFont(size=30), height=60, width=200, placeholder_text="555-1234")
        self.entry_telefono.pack(side="left", padx=5)
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(row2, text="Dirección:", font=ctk.CTkFont(size=25)).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row2, font=ctk.CTkFont(size=30), height=60, placeholder_text="Calle, Número, Ciudad")
        self.entry_direccion.pack(side="left", fill="x", expand=True, padx=5)
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(row3, text="➕ GUARDAR CLIENTE", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="green", command=self.guardar_cliente).pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkButton(row3, text="🗑️ BORRAR SELECCIONADO", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="red", command=self.borrar_cliente).pack(side="left", expand=True, fill="x", padx=10)
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Teléfono", "Dirección"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Nombre", text="Cliente"); self.tree.heading("Teléfono", text="Teléfono"); self.tree.heading("Dirección", text="Dirección")
        self.tree.column("ID", width=50); self.tree.column("Nombre", width=300)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

    def on_show(self):
        self.actualizar_tabla(); self.limpiar_campos()
    def guardar_cliente(self):
        nombre, telefono, direccion = self.entry_nombre.get().strip(), self.entry_telefono.get().strip(), self.entry_direccion.get().strip()
        if not nombre: return
        selected = self.tree.selection()
        if selected:
            self.controller.run_db_query("UPDATE clientes SET nombre=?, telefono=?, direccion=? WHERE id=?", (nombre, telefono, direccion, self.tree.item(selected[0])['values'][0]))
        else:
            self.controller.run_db_query("INSERT INTO clientes (nombre, telefono, direccion, google_id) VALUES (?, ?, ?, ?)", (nombre, telefono, direccion, None))
        self.actualizar_tabla(); self.limpiar_campos()
    def borrar_cliente(self):
        selected = self.tree.selection()
        if not selected: return
        if self.tree.item(selected[0])['values'][0] == 1: return
        if messagebox.askyesno("Confirmar", "¿Borrar cliente?"):
            self.controller.run_db_query("DELETE FROM clientes WHERE id=?", (self.tree.item(selected[0])['values'][0],))
            self.actualizar_tabla(); self.limpiar_campos()
    def actualizar_tabla(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.controller.run_db_query("SELECT id, nombre, telefono, direccion FROM clientes ORDER BY nombre ASC"): self.tree.insert("", "end", values=r)
    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end"); self.entry_telefono.delete(0, "end"); self.entry_direccion.delete(0, "end")
        for i in self.tree.get_children(): self.tree.selection_remove(i)

class FrameInventario(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()
        ctk.CTkLabel(self, text="📦 GESTIÓN DE INVENTARIO", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        form_frame.pack(padx=20, pady=10, fill="x")
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(row1, text="Producto:", font=ctk.CTkFont(size=25)).pack(side="left", padx=10)
        self.entry_nombre = ctk.CTkEntry(row1, font=ctk.CTkFont(size=30), height=60, placeholder_text="Ej: Taladro Bosch")
        self.entry_nombre.pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkLabel(row1, text="Precio ($):", font=ctk.CTkFont(size=25)).pack(side="left", padx=10)
        self.entry_precio = ctk.CTkEntry(row1, font=ctk.CTkFont(size=30), height=60, width=150, placeholder_text="0.00")
        self.entry_precio.pack(side="left", padx=10)
        ctk.CTkLabel(row1, text="Stock:", font=ctk.CTkFont(size=25)).pack(side="left", padx=10)
        self.entry_stock = ctk.CTkEntry(row1, font=ctk.CTkFont(size=30), height=60, width=150, placeholder_text="0")
        self.entry_stock.pack(side="left", padx=10)
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(row2, text="➕ AGREGAR / ACTUALIZAR", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="green", command=self.guardar_producto).pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkButton(row2, text="🗑️ BORRAR SELECCIONADO", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="red", command=self.borrar_producto).pack(side="left", expand=True, fill="x", padx=10)
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Nombre", text="Producto"); self.tree.heading("Precio", text="Precio"); self.tree.heading("Stock", text="Stock")
        self.tree.column("ID", width=50); self.tree.column("Nombre", width=400)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

    def on_show(self):
        self.actualizar_tabla(); self.limpiar_campos()
    def guardar_producto(self):
        nombre, p_txt, s_txt = self.entry_nombre.get().strip(), self.entry_precio.get().strip(), self.entry_stock.get().strip()
        if not nombre or not p_txt or not s_txt: return
        try: precio, stock = float(p_txt), int(s_txt)
        except: return
        selected = self.tree.selection()
        if selected:
            self.controller.run_db_query("UPDATE productos SET nombre=?, precio=?, stock=? WHERE id=?", (nombre, precio, stock, self.tree.item(selected[0])['values'][0]))
        else:
            self.controller.run_db_query("INSERT INTO productos (nombre, precio, stock, google_id) VALUES (?, ?, ?, ?)", (nombre, precio, stock, None))
        self.actualizar_tabla(); self.limpiar_campos()
    def borrar_producto(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Confirmar", "¿Borrar producto?"):
            self.controller.run_db_query("DELETE FROM productos WHERE id=?", (self.tree.item(selected[0])['values'][0],))
            self.actualizar_tabla(); self.limpiar_campos()
    def actualizar_tabla(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.controller.run_db_query("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre ASC"): self.tree.insert("", "end", values=r)
    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end"); self.entry_precio.delete(0, "end"); self.entry_stock.delete(0, "end")
        for i in self.tree.get_children(): self.tree.selection_remove(i)

class FrameVentas(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()
        ctk.CTkLabel(self, text="📋 HISTORIAL DE VENTAS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        self.tree = ttk.Treeview(self, columns=("ID", "Fecha", "Total", "Pago", "Vendedor"), show="headings")
        self.tree.heading("ID", text="Ticket"); self.tree.heading("Fecha", text="Fecha"); self.tree.heading("Total", text="Total"); self.tree.heading("Pago", text="Método"); self.tree.heading("Vendedor", text="Vendedor")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)
    def on_show(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = "SELECT v.id, v.fecha, v.total, v.tipo_pago, u.nombre FROM ventas v LEFT JOIN usuarios u ON v.usuario_id = u.id ORDER BY v.id DESC LIMIT 100"
        for r in self.controller.run_db_query(query): self.tree.insert("", "end", values=r)

class FrameFiado(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()
        ctk.CTkLabel(self, text="📖 LIBRETA DE FIADOS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        self.tree = ttk.Treeview(self, columns=("ID", "Cliente", "Monto", "Fecha", "Estado"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Cliente", text="Cliente"); self.tree.heading("Monto", text="Debe"); self.tree.heading("Fecha", text="Fecha"); self.tree.heading("Estado", text="Estado")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent"); btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="MARCAR COMO PAGADO", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="green", command=self.marcar_pagado).grid(row=0, column=0, padx=20)
        ctk.CTkButton(btn_frame, text="VOLVER", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).grid(row=0, column=1, padx=20)
    def on_show(self): self.actualizar_fiados()
    def actualizar_fiados(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = "SELECT f.id, c.nombre, f.monto, f.fecha, CASE WHEN f.pagado=1 THEN 'PAGADO' ELSE 'DEBE' END FROM fiados f LEFT JOIN clientes c ON f.cliente_id = c.id ORDER BY f.pagado ASC, f.id DESC"
        for r in self.controller.run_db_query(query): self.tree.insert("", "end", values=(r[0], r[1] or "Final", r[2], r[3], r[4]))
    def marcar_pagado(self):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])['values']
        if item[4] == "PAGADO": return
        self.controller.run_db_query("UPDATE fiados SET pagado = 1 WHERE id = ?", (item[0],))
        self.actualizar_fiados()

class FrameCierre(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="💰 CORTE DE CAJA (CIERRE DIARIO)", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        self.info_frame = ctk.CTkFrame(self, fg_color="#2b2b2b"); self.info_frame.pack(padx=50, pady=20, fill="x")
        ctk.CTkButton(self, text="GENERAR REPORTE DE HOY", font=ctk.CTkFont(size=35, weight="bold"), height=100, fg_color="blue", command=self.generar_corte).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)
    def generar_corte(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        t_ef = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Efectivo'", (f"{hoy}%",)).fetchone()[0]
        t_ta = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Tarjeta'", (f"{hoy}%",)).fetchone()[0]
        t_fi = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Fiado'", (f"{hoy}%",)).fetchone()[0]
        n_v = self.controller.run_db_query("SELECT COUNT(*) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",)).fetchone()[0]
        for w in self.info_frame.winfo_children(): w.destroy()
        for t in [f"Fecha: {hoy}", f"Ventas: {n_v}", f"Efectivo: ${t_ef:.2f}", f"Tarjeta: ${t_ta:.2f}", f"Fiado: ${t_fi:.2f}", f"GRAN TOTAL: ${t_ef+t_ta+t_fi:.2f}"]:
            ctk.CTkLabel(self.info_frame, text=t, font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10, padx=20, anchor="w")

if __name__ == "__main__":
    app = FerreteriaTPV()
    app.mainloop()