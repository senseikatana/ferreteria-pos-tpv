import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os

# --- CONFIGURACIÓN VISUAL PARA GUANTES Y TÁCTIL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FerreteriaTPV(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ TPV FERRETERÍA ⚡")
        self.geometry("1280x800")
        self.attributes('-fullscreen', True) # Pantalla completa
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False)) # Esc para salir de pantalla completa
        
        self.db_name = "ferreteria.db"
        self.init_db()
        
        self.carrito = []
        self.total_actual = 0.0

        # Contenedor principal para cambiar de pantallas
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        # Registro de todas las pantallas
        for F in (MenuPrincipal, FrameCaja, FrameClientes, FrameVentas, FrameFiado, FrameCierre, FrameInventario):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuPrincipal")

    def init_db(self):
        """Crea la base de datos y actualiza el esquema para CRM y Google Sync"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de Productos (Con google_id para futura sincronización)
        cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                          (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL, stock INTEGER, google_id TEXT)''')
        
        # Tabla de Clientes / CRM (Con google_id para futura sincronización)
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                          (id INTEGER PRIMARY KEY, nombre TEXT, telefono TEXT, direccion TEXT, google_id TEXT)''')
        
        # Tabla de Ventas
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id INTEGER PRIMARY KEY, fecha TEXT, total REAL, tipo_pago TEXT)''')
                          
        # Tabla Detalles Venta
        cursor.execute('''CREATE TABLE IF NOT EXISTS detalles_venta 
                          (id INTEGER PRIMARY KEY, venta_id INTEGER, producto TEXT, cantidad INTEGER, subtotal REAL)''')
        
        # Tabla Fiados (Ahora vinculada a client_id en lugar de texto libre)
        cursor.execute('''CREATE TABLE IF NOT EXISTS fiados 
                          (id INTEGER PRIMARY KEY, cliente_id INTEGER, monto REAL, fecha TEXT, pagado INTEGER)''')
        
        # --- MIGRACIÓN SEGURA (Si la DB ya existía, agregamos las columnas que faltan sin borrar datos) ---
        try:
            cursor.execute("ALTER TABLE productos ADD COLUMN google_id TEXT")
        except sqlite3.OperationalError:
            pass # La columna ya existe
            
        try:
            cursor.execute("ALTER TABLE fiados ADD COLUMN cliente_id INTEGER")
        except sqlite3.OperationalError:
            pass # La columna ya existe

        # Productos de ejemplo si está vacío
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            productos_ejemplo = [
                ("Martillo", 15.50, 50, None), ("Caja Tornillos 1/4", 8.00, 100, None),
                ("Taladro Percutor", 85.00, 10, None), ("Cemento 50kg", 12.00, 200, None),
                ("Pintura Blanca 4L", 25.00, 30, None), ("Cable 2x1.5 (metro)", 1.50, 500, None)
            ]
            cursor.executemany("INSERT INTO productos (nombre, precio, stock, google_id) VALUES (?, ?, ?, ?)", productos_ejemplo)
            
        # Cliente de ejemplo
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
        """Configuración centralizada para tablas oscuras y táctiles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b",
                        font=("Arial", 22, "bold"), 
                        rowheight=70,
                        borderwidth=0)
        style.map("Treeview", 
                  background=[('selected', '#FFD700')], 
                  foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", 
                        background="#404040", 
                        foreground="white",
                        font=("Arial", 24, "bold"),
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', '#404040')])


class MenuPrincipal(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="🛠️ TPV FERRETERÍA 🛠️", font=ctk.CTkFont(size=50, weight="bold")).pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", padx=50, pady=10)

        botones = [
            ("1. CAJA / VENDER (F1)", "FrameCaja", "green"),
            ("2. CLIENTES / CRM (F2)", "FrameClientes", "#1ABC9C"),
            ("3. HISTORIAL VENTAS (F3)", "FrameVentas", "blue"),
            ("4. FIADOS (F4)", "FrameFiado", "orange"),
            ("5. CIERRE DE CAJA (F5)", "FrameCierre", "red"),
            ("6. INVENTARIO (F8)", "FrameInventario", "#8E44AD"),
            ("SALIR (ESC)", None, "gray")
        ]

        for i, (texto, frame, color) in enumerate(botones):
            btn = ctk.CTkButton(
                btn_frame, 
                text=texto, 
                font=ctk.CTkFont(size=32, weight="bold"), 
                height=75,
                fg_color=color,
                hover_color="white",
                text_color_disabled="black",
                command=lambda f=frame: self.navegar(f) if f else self.controller.destroy()
            )
            btn.grid(row=i, column=0, pady=8, padx=50, sticky="ew")
            
            if i == 0: self.controller.bind("<F1>", lambda e: self.navegar("FrameCaja"))
            if i == 1: self.controller.bind("<F2>", lambda e: self.navegar("FrameClientes"))
            if i == 2: self.controller.bind("<F3>", lambda e: self.navegar("FrameVentas"))
            if i == 3: self.controller.bind("<F4>", lambda e: self.navegar("FrameFiado"))
            if i == 4: self.controller.bind("<F5>", lambda e: self.navegar("FrameCierre"))
            if i == 5: self.controller.bind("<F8>", lambda e: self.navegar("FrameInventario"))

        btn_frame.columnconfigure(0, weight=1)

    def navegar(self, frame):
        self.controller.show_frame(frame)

class FrameCaja(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()

        # Configuración de columnas: Izquierda (Productos) ancha, Derecha (Ticket y Botones) fija
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

        # Tabla de productos
        self.tree_productos = ttk.Treeview(left_frame, columns=("Nombre", "Precio", "Stock"), show="headings")
        self.tree_productos.heading("Nombre", text="PRODUCTO")
        self.tree_productos.heading("Precio", text="PRECIO $")
        self.tree_productos.heading("Stock", text="STOCK")
        
        # Ajuste de columnas para que se vean gigantes
        self.tree_productos.column("Nombre", width=400, stretch=True)
        self.tree_productos.column("Precio", width=150, anchor="center")
        self.tree_productos.column("Stock", width=150, anchor="center")
        
        self.tree_productos.pack(fill="both", expand=True)
        
        # EVENTO TÁCTIL PURO: <Button-1> se dispara al instante al tocar con el dedo o ratón
        self.tree_productos.bind("<Button-1>", self.agregar_al_carrito)

        # --- DERECHA: TICKET Y BOTONES EN COLUMNA ---
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        ctk.CTkLabel(right_frame, text="🛒 TICKET ACTUAL", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(10, 5))

        # Tabla del carrito
        self.tree_carrito = ttk.Treeview(right_frame, columns=("Prod", "Cant", "Subtotal"), show="headings", height=8)
        self.tree_carrito.heading("Prod", text="Producto")
        self.tree_carrito.heading("Cant", text="Cant")
        self.tree_carrito.heading("Subtotal", text="Total")
        self.tree_carrito.column("Prod", width=200, stretch=True)
        self.tree_carrito.column("Cant", width=50, anchor="center")
        self.tree_carrito.column("Subtotal", width=100, anchor="center")
        self.tree_carrito.pack(fill="both", expand=True, padx=10)
        
        # TOTAL GIGANTE
        self.lbl_total = ctk.CTkLabel(right_frame, text="TOTAL: $0.00", font=ctk.CTkFont(size=55, weight="bold"), text_color="yellow")
        self.lbl_total.pack(pady=15)

        # BOTONES EN COLUMNA (Uno debajo del otro, ocupando todo el ancho)
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Fila 1: Cobros
        row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkButton(row1, text="💵 COBRAR EFECTIVO (F9)", font=ctk.CTkFont(size=26, weight="bold"), height=80, fg_color="green", command=lambda: self.cobrar("Efectivo")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(row1, text="💳 COBRAR TARJETA (F10)", font=ctk.CTkFont(size=26, weight="bold"), height=80, fg_color="blue", command=lambda: self.cobrar("Tarjeta")).pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Fila 2: Fiar
        ctk.CTkButton(btn_frame, text="📖 FIAR A CLIENTE (F11)", font=ctk.CTkFont(size=28, weight="bold"), height=80, fg_color="orange", command=self.fiar).pack(fill="x", pady=5)

        # Fila 3: Borrar del ticket
        ctk.CTkButton(btn_frame, text="❌ BORRAR DEL TICKET (Supr)", font=ctk.CTkFont(size=24, weight="bold"), height=70, fg_color="red", command=self.borrar_del_carrito).pack(fill="x", pady=5)

        # Fila 4: Volver
        ctk.CTkButton(btn_frame, text="🏠 VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=24, weight="bold"), height=70, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(fill="x", pady=5)

        # --- ATAJOS DE TECLADO SEGUROS ---
        # Solo funcionan si esta pantalla está visible (winfo_ismapped)
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
        
        # Seleccionamos solo las columnas que mostramos ahora
        query = "SELECT nombre, precio, stock FROM productos WHERE nombre LIKE ? ORDER BY nombre ASC"
        rows = self.controller.run_db_query(query, (f"%{filtro}%",))
        for row in rows:
            self.tree_productos.insert("", "end", values=row)

    def agregar_al_carrito(self, event):
        # Identificar qué fila fue tocada
        region = self.tree_productos.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item_id = self.tree_productos.identify_row(event.y)
        if not item_id:
            return
            
        self.tree_productos.selection_set(item_id)
        selected = self.tree_productos.selection()
        
        if not selected: return
        
        # Obtenemos los valores: (Nombre, Precio, Stock)
        values = self.tree_productos.item(selected[0])['values']
        nombre, precio, stock = values
        
        # Necesitamos el ID real del producto para descontar stock luego. Lo buscamos rápido.
        prod_data = self.controller.run_db_query("SELECT id FROM productos WHERE nombre=? AND precio=?", (nombre, precio)).fetchone()
        if not prod_data: return
        prod_id = prod_data[0]

        self._agregar_item((prod_id, nombre, precio, stock))

    def _agregar_item(self, item):
        prod_id, nombre, precio, stock = item
        
        # Validación de stock
        if stock <= 0:
            messagebox.showwarning("Sin Stock", f"¡Cuidado! No hay existencia de {nombre}")
            return
        
        encontrado = False
        for i in self.carrito:
            if i[0] == prod_id:
                i[2] += 1 # Aumentar cantidad
                i[4] = round(i[2] * float(precio), 2) # Recalcular subtotal
                encontrado = True
                break
        
        if not encontrado:
            # [id, nombre, cantidad, precio_unitario, subtotal]
            self.carrito.append([prod_id, nombre, 1, float(precio), round(float(precio), 2)])
        
        self.actualizar_carrito_ui()

    def borrar_del_carrito(self):
        """Borra el último producto agregado o el seleccionado"""
        selected = self.tree_carrito.selection()
        if selected:
            index = self.tree_carrito.index(selected[0])
            if 0 <= index < len(self.carrito):
                self.carrito.pop(index)
        elif self.carrito:
            # Si no hay nada seleccionado, borra el último (útil para teclado rápido)
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
        if not self.carrito:
            return # No hacer nada si está vacío, sin molestar con popups
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago) VALUES (?, ?, ?)", (fecha, self.total_actual, metodo))
        venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]

        for item in self.carrito:
            self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                                         (venta_id, item[1], item[2], item[4]))
            self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

        messagebox.showinfo("¡Venta Exitosa!", f"Cobrado: ${self.total_actual:.2f}\nMétodo: {metodo}")
        self.carrito = []
        self.actualizar_carrito_ui()
        self.actualizar_productos()
        self.entry_buscar.delete(0, "end")

    def fiar(self):
        if not self.carrito:
            return
        
        rows = self.controller.run_db_query("SELECT id, nombre FROM clientes ORDER BY nombre ASC").fetchall()
        if not rows:
            messagebox.showerror("Error", "No hay clientes. Ve al CRM (F2) primero.")
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
            
            self.controller.run_db_query("INSERT INTO fiados (cliente_id, monto, fecha, pagado) VALUES (?, ?, ?, ?)",
                                         (cliente_id, self.total_actual, fecha, 0))
            
            self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago) VALUES (?, ?, ?)", (fecha, self.total_actual, "Fiado"))
            venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]
            
            for item in self.carrito:
                self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                                             (venta_id, item[1], item[2], item[4]))
                self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

            messagebox.showinfo("Fiado OK", f"Deuda de ${self.total_actual:.2f} registrada.", parent=dialog)
            self.carrito = []
            self.actualizar_carrito_ui()
            self.actualizar_productos()
            self.entry_buscar.delete(0, "end")
            dialog.destroy()

        ctk.CTkButton(dialog, text="✅ CONFIRMAR FIADO", font=ctk.CTkFont(size=30, weight="bold"), height=90, fg_color="orange", command=confirmar_fiado).pack(pady=20, padx=20, fill="x")






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

        ctk.CTkButton(row3, text="➕ GUARDAR CLIENTE (Enter)", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="green", command=self.guardar_cliente).pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkButton(row3, text="🗑️ BORRAR SELECCIONADO (Supr)", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="red", command=self.borrar_cliente).pack(side="left", expand=True, fill="x", padx=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Teléfono", "Dirección"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Cliente")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Dirección", text="Dirección")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=300)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # CORREGIDO: self.controller
        ctk.CTkButton(self, text="VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

        self.controller.bind("<Return>", self.guardar_cliente_enter)
        self.controller.bind("<Delete>", lambda e: self.borrar_cliente() if self.winfo_ismapped() else None)

    def on_show(self):
        self.actualizar_tabla()
        self.limpiar_campos()
        self.entry_nombre.focus_set()

    def guardar_cliente_enter(self, event):
        if self.controller.frames["FrameClientes"].winfo_ismapped():
            self.guardar_cliente()

    def guardar_cliente(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        direccion = self.entry_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Faltan datos", "El cliente debe tener un nombre.")
            return

        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            self.controller.run_db_query("UPDATE clientes SET nombre=?, telefono=?, direccion=? WHERE id=?", (nombre, telefono, direccion, item_id))
            messagebox.showinfo("Éxito", "Cliente actualizado.")
        else:
            self.controller.run_db_query("INSERT INTO clientes (nombre, telefono, direccion, google_id) VALUES (?, ?, ?, ?)", (nombre, telefono, direccion, None))
            messagebox.showinfo("Éxito", "Cliente agregado al CRM.")

        self.actualizar_tabla()
        self.limpiar_campos()

    def borrar_cliente(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_id = self.tree.item(selected[0])['values'][0]
        if item_id == 1:
            messagebox.showerror("Protegido", "No puedes borrar al 'Consumidor Final'.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Borrar este cliente?"):
            self.controller.run_db_query("DELETE FROM clientes WHERE id=?", (item_id,))
            self.actualizar_tabla()
            self.limpiar_campos()

    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.controller.run_db_query("SELECT id, nombre, telefono, direccion FROM clientes ORDER BY nombre ASC")
        for row in rows:
            self.tree.insert("", "end", values=row)

    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_direccion.delete(0, "end")
        for item in self.tree.get_children():
            self.tree.selection_remove(item)


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

        ctk.CTkButton(row2, text="➕ AGREGAR / ACTUALIZAR (Enter)", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="green", command=self.guardar_producto).pack(side="left", expand=True, fill="x", padx=10)
        ctk.CTkButton(row2, text="🗑️ BORRAR SELECCIONADO (Supr)", font=ctk.CTkFont(size=25, weight="bold"), height=80, fg_color="red", command=self.borrar_producto).pack(side="left", expand=True, fill="x", padx=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Producto")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=400)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(self, text="VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

        self.controller.bind("<Return>", self.guardar_producto_enter)
        self.controller.bind("<Delete>", lambda e: self.borrar_producto() if self.winfo_ismapped() else None)

    def on_show(self):
        self.actualizar_tabla()
        self.limpiar_campos()
        self.entry_nombre.focus_set()

    def guardar_producto_enter(self, event):
        # ESTO EVITA QUE EL ENTER DE LA CAJA DISPARE EL INVENTARIO
        if self.controller.frames["FrameInventario"].winfo_ismapped():
            self.guardar_producto()

    def guardar_producto(self):
        nombre = self.entry_nombre.get().strip()
        precio_txt = self.entry_precio.get().strip()
        stock_txt = self.entry_stock.get().strip()

        if not nombre or not precio_txt or not stock_txt:
            messagebox.showwarning("Faltan datos", "Por favor llena el nombre, precio y stock.")
            return

        try:
            precio = float(precio_txt)
            stock = int(stock_txt)
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser números válidos.")
            return

        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            self.controller.run_db_query("UPDATE productos SET nombre=?, precio=?, stock=? WHERE id=?", (nombre, precio, stock, item_id))
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        else:
            self.controller.run_db_query("INSERT INTO productos (nombre, precio, stock, google_id) VALUES (?, ?, ?, ?)", (nombre, precio, stock, None))
            messagebox.showinfo("Éxito", "Producto agregado al inventario.")

        self.actualizar_tabla()
        self.limpiar_campos()

    def borrar_producto(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecciona un producto de la lista para borrarlo.")
            return
        
        item_id = self.tree.item(selected[0])['values'][0]
        nombre = self.tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirmar Borrado", f"¿Estás seguro de borrar '{nombre}'?\nEsta acción no se puede deshacer."):
            self.controller.run_db_query("DELETE FROM productos WHERE id=?", (item_id,))
            self.actualizar_tabla()
            self.limpiar_campos()

    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.controller.run_db_query("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre ASC")
        for row in rows:
            self.tree.insert("", "end", values=row)

    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.entry_stock.delete(0, "end")
        for item in self.tree.get_children():
            self.tree.selection_remove(item)


class FrameVentas(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()

        ctk.CTkLabel(self, text="📋 HISTORIAL DE VENTAS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)

        self.tree = ttk.Treeview(self, columns=("ID", "Fecha", "Total", "Pago"), show="headings")
        self.tree.heading("ID", text="Ticket")
        self.tree.heading("Fecha", text="Fecha y Hora")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Pago", text="Método")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(self, text="VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, 
                      command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

    def on_show(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.controller.run_db_query("SELECT * FROM ventas ORDER BY id DESC LIMIT 100")
        for row in rows:
            self.tree.insert("", "end", values=row)


class FrameFiado(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.get_estilos_tabla()

        ctk.CTkLabel(self, text="📖 LIBRETA DE FIADOS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)

        self.tree = ttk.Treeview(self, columns=("ID", "Cliente", "Monto", "Fecha", "Estado"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Monto", text="Debe")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Estado", text="Estado")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="MARCAR COMO PAGADO (Enter)", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="green", command=self.marcar_pagado).grid(row=0, column=0, padx=20)
        ctk.CTkButton(btn_frame, text="VOLVER (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).grid(row=0, column=1, padx=20)

    def on_show(self):
        self.actualizar_fiados()

    def actualizar_fiados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = """
            SELECT f.id, c.nombre, f.monto, f.fecha, CASE WHEN f.pagado=1 THEN 'PAGADO' ELSE 'DEBE' END 
            FROM fiados f 
            LEFT JOIN clientes c ON f.cliente_id = c.id 
            ORDER BY f.pagado ASC, f.id DESC
        """
        rows = self.controller.run_db_query(query)
        for row in rows:
            nombre_cliente = row[1] if row[1] else "Consumidor Final"
            self.tree.insert("", "end", values=(row[0], nombre_cliente, row[2], row[3], row[4]))

    def marcar_pagado(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecciona un fiado de la lista.")
            return
        item = self.tree.item(selected[0])['values']
        fiado_id = item[0]
        
        if item[4] == "PAGADO":
            messagebox.showinfo("Info", "Este fiado ya fue pagado.")
            return

        self.controller.run_db_query("UPDATE fiados SET pagado = 1 WHERE id = ?", (fiado_id,))
        messagebox.showinfo("Éxito", f"Fiado de {item[1]} marcado como pagado.")
        self.actualizar_fiados()


class FrameCierre(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="💰 CORTE DE CAJA (CIERRE DIARIO)", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)

        self.info_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.info_frame.pack(padx=50, pady=20, fill="x")

        ctk.CTkButton(self, text="GENERAR REPORTE DE HOY", font=ctk.CTkFont(size=35, weight="bold"), height=100, fg_color="blue", command=self.generar_corte).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: self.controller.show_frame("MenuPrincipal")).pack(pady=20)

    def generar_corte(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        total_efectivo = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Efectivo'", (f"{hoy}%",)).fetchone()[0]
        total_tarjeta = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Tarjeta'", (f"{hoy}%",)).fetchone()[0]
        total_fiado = self.controller.run_db_query("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ? AND tipo_pago='Fiado'", (f"{hoy}%",)).fetchone()[0]
        num_ventas = self.controller.run_db_query("SELECT COUNT(*) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",)).fetchone()[0]

        for widget in self.info_frame.winfo_children():
            widget.destroy()

        textos = [
            f"Fecha de Corte: {hoy}",
            f"Número de Ventas Hoy: {num_ventas}",
            f"Total Efectivo: ${total_efectivo:.2f}",
            f"Total Tarjeta: ${total_tarjeta:.2f}",
            f"Total Fiado Hoy: ${total_fiado:.2f}",
            f"GRAN TOTAL DEL DÍA: ${total_efectivo + total_tarjeta + total_fiado:.2f}"
        ]

        for texto in textos:
            ctk.CTkLabel(self.info_frame, text=texto, font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10, padx=20, anchor="w")


if __name__ == "__main__":
    app = FerreteriaTPV()
    app.mainloop()