import customtkinter as ctk
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
        for F in (MenuPrincipal, FrameCaja, FrameVentas, FrameFiado, FrameCierre):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuPrincipal")

    def init_db(self):
        """Crea la base de datos si no existe"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                          (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL, stock INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id INTEGER PRIMARY KEY, fecha TEXT, total REAL, tipo_pago TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS detalles_venta 
                          (id INTEGER PRIMARY KEY, venta_id INTEGER, producto TEXT, cantidad INTEGER, subtotal REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS fiados 
                          (id INTEGER PRIMARY KEY, cliente TEXT, monto REAL, fecha TEXT, pagado INTEGER)''')
        
        # Productos de ejemplo si está vacío
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            productos_ejemplo = [
                ("Martillo", 15.50, 50), ("Caja Tornillos 1/4", 8.00, 100),
                ("Taladro Percutor", 85.00, 10), ("Cemento 50kg", 12.00, 200),
                ("Pintura Blanca 4L", 25.00, 30), ("Cable 2x1.5 (metro)", 1.50, 500)
            ]
            cursor.executemany("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)", productos_ejemplo)
        
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

class MenuPrincipal(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="🛠️ TPV FERRETERÍA 🛠️", font=ctk.CTkFont(size=60, weight="bold")).pack(pady=50)

        # Botones Gigantes para uso con guantes
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", padx=50, pady=20)

        botones = [
            ("1. CAJA (F1)", "FrameCaja", "green"),
            ("2. HISTORIAL VENTAS (F2)", "FrameVentas", "blue"),
            ("3. FIADOS (F3)", "FrameFiado", "orange"),
            ("4. CIERRE DE CAJA (F4)", "FrameCierre", "red"),
            ("SALIR (ESC)", None, "gray")
        ]

        for i, (texto, frame, color) in enumerate(botones):
            btn = ctk.CTkButton(
                btn_frame, 
                text=texto, 
                font=ctk.CTkFont(size=45, weight="bold"),
                height=120,
                fg_color=color,
                hover_color="white",
                text_color_disabled="black",
                command=lambda f=frame: self.navegar(f) if f else self.controller.destroy()
            )
            btn.grid(row=i, column=0, pady=20, padx=50, sticky="ew")
            
            # Atajos de teclado
            if i == 0: self.controller.bind("<F1>", lambda e: self.navegar("FrameCaja"))
            if i == 1: self.controller.bind("<F2>", lambda e: self.navegar("FrameVentas"))
            if i == 2: self.controller.bind("<F3>", lambda e: self.navegar("FrameFiado"))
            if i == 3: self.controller.bind("<F4>", lambda e: self.navegar("FrameCierre"))

        btn_frame.columnconfigure(0, weight=1)

    def navegar(self, frame):
        self.controller.show_frame(frame)


class FrameCaja(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout: Izquierda (Productos), Derecha (Carrito y Total)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        # --- IZQUIERDA: PRODUCTOS ---
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="PRODUCTOS", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10)
        
        # Barra de búsqueda rápida
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10)
        ctk.CTkLabel(search_frame, text="Buscar (Teclea y Enter):", font=ctk.CTkFont(size=20)).pack(side="left")
        self.entry_buscar = ctk.CTkEntry(search_frame, font=ctk.CTkFont(size=25), height=50)
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=10)
        self.entry_buscar.bind("<Return>", self.buscar_producto)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_producto)

        # Tabla de productos (Treeview estilizado)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=("Arial", 18), rowheight=50)
        style.configure("Treeview.Heading", font=("Arial", 20, "bold"))
        
        self.tree_productos = ttk.Treeview(left_frame, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree_productos.heading("ID", text="ID")
        self.tree_productos.heading("Nombre", text="Producto")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Stock", text="Stock")
        self.tree_productos.column("ID", width=50)
        self.tree_productos.column("Nombre", width=300)
        self.tree_productos.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Doble clic o Enter para agregar al carrito
        self.tree_productos.bind("<Double-1>", self.agregar_al_carrito)
        self.controller.bind("<Return>", self.agregar_al_carrito_teclado)

        # --- DERECHA: CARRITO Y COBRO ---
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="TICKET / CARRITO", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10)

        self.tree_carrito = ttk.Treeview(right_frame, columns=("Prod", "Cant", "Subtotal"), show="headings")
        self.tree_carrito.heading("Prod", text="Producto")
        self.tree_carrito.heading("Cant", text="Cant")
        self.tree_carrito.heading("Subtotal", text="Total")
        self.tree_carrito.pack(fill="both", expand=True, padx=10)

        self.lbl_total = ctk.CTkLabel(right_frame, text="TOTAL: $0.00", font=ctk.CTkFont(size=50, weight="bold"), text_color="yellow")
        self.lbl_total.pack(pady=20)

        # Botones de acción inferiores
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="COBRAR\nefectivo (F5)", font=ctk.CTkFont(size=25, weight="bold"), height=100, fg_color="green", command=lambda: self.cobrar("Efectivo")).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="COBRAR\ntarjeta (F6)", font=ctk.CTkFont(size=25, weight="bold"), height=100, fg_color="blue", command=lambda: self.cobrar("Tarjeta")).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="FIAR\n(F7)", font=ctk.CTkFont(size=25, weight="bold"), height=100, fg_color="orange", command=self.fiar).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="VOLVER\n(Esc)", font=ctk.CTkFont(size=25, weight="bold"), height=100, fg_color="gray", command=lambda: controller.show_frame("MenuPrincipal")).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.controller.bind("<F5>", lambda e: self.cobrar("Efectivo"))
        self.controller.bind("<F6>", lambda e: self.cobrar("Tarjeta"))
        self.controller.bind("<F7>", lambda e: self.fiar())

    def on_show(self):
        self.actualizar_productos()
        self.carrito = []
        self.actualizar_carrito_ui()
        self.entry_buscar.focus_set()

    def buscar_producto(self, event=None):
        self.actualizar_productos(self.entry_buscar.get())

    def actualizar_productos(self, filtro=""):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        query = "SELECT * FROM productos WHERE nombre LIKE ?"
        rows = self.controller.run_db_query(query, (f"%{filtro}%",))
        for row in rows:
            self.tree_productos.insert("", "end", values=row)

    def agregar_al_carrito(self, event):
        selected = self.tree_productos.selection()
        if not selected: return
        item = self.tree_productos.item(selected[0])['values']
        self._agregar_item(item)

    def agregar_al_carrito_teclado(self, event):
        # Solo si estamos en esta pantalla
        if self.controller.frames["FrameCaja"].winfo_ismapped():
            selected = self.tree_productos.selection()
            if selected:
                item = self.tree_productos.item(selected[0])['values']
                self._agregar_item(item)

    def _agregar_item(self, item):
        prod_id, nombre, precio, stock = item
        if stock <= 0:
            messagebox.showwarning("Sin Stock", f"No hay existencia de {nombre}")
            return
        
        # Buscar si ya está en el carrito
        encontrado = False
        for i in self.carrito:
            if i[0] == prod_id:
                i[2] += 1
                i[3] = round(i[2] * precio, 2)
                encontrado = True
                break
        
        if not encontrado:
            self.carrito.append([prod_id, nombre, 1, precio, round(precio, 2)])
        
        self.actualizar_carrito_ui()

    def actualizar_carrito_ui(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        total = 0
        for item in self.carrito:
            # item: [id, nombre, cantidad, precio_unitario, subtotal]
            self.tree_carrito.insert("", "end", values=(item[1], item[2], f"${item[4]:.2f}"))
            total += item[4]
        
        self.lbl_total.configure(text=f"TOTAL: ${total:.2f}")
        self.total_actual = total

    def cobrar(self, metodo):
        if not self.carrito:
            messagebox.showinfo("Vacío", "Agrega productos primero.")
            return
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago) VALUES (?, ?, ?)", (fecha, self.total_actual, metodo))
        venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]

        for item in self.carrito:
            self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                                         (venta_id, item[1], item[2], item[4]))
            # Descontar stock
            self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

        messagebox.showinfo("Venta Exitosa", f"Venta registrada.\nTotal: ${self.total_actual:.2f}\nMétodo: {metodo}")
        self.carrito = []
        self.actualizar_carrito_ui()
        self.actualizar_productos()
        self.entry_buscar.delete(0, "end")

    def fiar(self):
        if not self.carrito:
            messagebox.showinfo("Vacío", "Agrega productos primero.")
            return
        
        dialog = ctk.CTkInputDialog(text="Nombre del Cliente (Fiado):", title="Registrar Fiado", font=ctk.CTkFont(size=30))
        cliente = dialog.get_input()
        
        if cliente:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.controller.run_db_query("INSERT INTO fiados (cliente, monto, fecha, pagado) VALUES (?, ?, ?, ?)",
                                         (cliente, self.total_actual, fecha, 0))
            
            # También registrar como venta pero marcada como fiado
            self.controller.run_db_query("INSERT INTO ventas (fecha, total, tipo_pago) VALUES (?, ?, ?)", (fecha, self.total_actual, "Fiado"))
            venta_id = self.controller.run_db_query("SELECT last_insert_rowid()").fetchone()[0]
            for item in self.carrito:
                self.controller.run_db_query("INSERT INTO detalles_venta (venta_id, producto, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                                             (venta_id, item[1], item[2], item[4]))
                self.controller.run_db_query("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))

            messagebox.showinfo("Fiado Registrado", f"Se fió ${self.total_actual:.2f} a {cliente}")
            self.carrito = []
            self.actualizar_carrito_ui()
            self.actualizar_productos()
            self.entry_buscar.delete(0, "end")


class FrameVentas(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="📋 HISTORIAL DE VENTAS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 20), rowheight=50)
        
        self.tree = ttk.Treeview(self, columns=("ID", "Fecha", "Total", "Pago"), show="headings")
        self.tree.heading("ID", text="Ticket")
        self.tree.heading("Fecha", text="Fecha y Hora")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Pago", text="Método")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(self, text="VOLVER AL MENÚ (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, 
                      command=lambda: controller.show_frame("MenuPrincipal")).pack(pady=20)

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

        ctk.CTkLabel(self, text="📖 LIBRETA DE FIADOS", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 20), rowheight=50)
        
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
        ctk.CTkButton(btn_frame, text="VOLVER (Esc)", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: controller.show_frame("MenuPrincipal")).grid(row=0, column=1, padx=20)

    def on_show(self):
        self.actualizar_fiados()

    def actualizar_fiados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.controller.run_db_query("SELECT id, cliente, monto, fecha, CASE WHEN pagado=1 THEN 'PAGADO' ELSE 'DEBE' END FROM fiados ORDER BY pagado ASC, id DESC")
        for row in rows:
            self.tree.insert("", "end", values=row)

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
        ctk.CTkButton(self, text="VOLVER AL MENÚ", font=ctk.CTkFont(size=30, weight="bold"), height=80, fg_color="gray", command=lambda: controller.show_frame("MenuPrincipal")).pack(pady=20)

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