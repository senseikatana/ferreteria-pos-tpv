"""
Pantalla de venta (Punto de Venta).

Flujo:
1. El cajero escribe/escanea el código de barras y presiona Enter
   (una pistola lectora de código de barras funciona exactamente
   como un teclado que "escribe rápido y presiona Enter", así que
   este mismo campo funciona con lector físico o tecleo manual).
2. El producto se agrega al carrito (o se suma 1 si ya estaba).
3. Se puede ajustar cantidad o quitar productos del carrito.
4. Se elige forma de pago: efectivo, tarjeta o fiado.
   - Si es fiado, se debe elegir un cliente registrado.
5. Se confirma la venta: se descuenta stock, se guarda en la base
   y se limpia el carrito para la siguiente venta.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk

from database import db
from config import MONEDA


class VistaVenta(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        self.carrito = []  # lista de dicts: producto_id, nombre, cantidad, precio_unitario, subtotal
        self.cliente_seleccionado_id = None

        self._construir_ui()
        self._refrescar_carrito()

    # -----------------------------------------------------------------
    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Panel izquierdo: escaneo + carrito ----------------
        panel_izq = ctk.CTkFrame(self, corner_radius=12)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel_izq.grid_rowconfigure(2, weight=1)
        panel_izq.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel_izq, text="Punto de venta",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        frame_scan = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_scan.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        frame_scan.grid_columnconfigure(0, weight=1)

        self.entry_codigo = ctk.CTkEntry(
            frame_scan,
            placeholder_text="Escanea o escribe el código de barras y presiona Enter…",
            height=40,
        )
        self.entry_codigo.grid(row=0, column=0, sticky="ew")
        self.entry_codigo.bind("<Return>", lambda e: self._agregar_por_codigo())
        self.entry_codigo.focus()

        ctk.CTkButton(
            frame_scan, text="Agregar", width=90, height=40,
            command=self._agregar_por_codigo,
        ).grid(row=0, column=1, padx=(8, 0))

        # Tabla del carrito
        frame_tabla = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_tabla.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Carrito.Treeview", rowheight=28, font=("Segoe UI", 11),
            background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white",
        )
        estilo.configure("Carrito.Treeview.Heading", font=("Segoe UI", 11, "bold"))

        columnas = ("producto", "cantidad", "precio", "subtotal")
        self.tabla_carrito = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings",
            style="Carrito.Treeview", selectmode="browse",
        )
        self.tabla_carrito.heading("producto", text="Producto")
        self.tabla_carrito.heading("cantidad", text="Cant.")
        self.tabla_carrito.heading("precio", text="Precio")
        self.tabla_carrito.heading("subtotal", text="Subtotal")
        self.tabla_carrito.column("producto", width=260)
        self.tabla_carrito.column("cantidad", width=60, anchor="center")
        self.tabla_carrito.column("precio", width=90, anchor="e")
        self.tabla_carrito.column("subtotal", width=100, anchor="e")
        self.tabla_carrito.grid(row=0, column=0, sticky="nsew")

        frame_botones_item = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_botones_item.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))

        ctk.CTkButton(
            frame_botones_item, text="+1", width=50,
            command=lambda: self._cambiar_cantidad(1),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            frame_botones_item, text="-1", width=50,
            command=lambda: self._cambiar_cantidad(-1),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            frame_botones_item, text="Quitar producto", width=140,
            fg_color="#c0392b", hover_color="#922b21",
            command=self._quitar_seleccionado,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            frame_botones_item, text="Vaciar carrito", width=120,
            fg_color="transparent", border_width=1,
            command=self._vaciar_carrito,
        ).pack(side="left")

        # ---------------- Panel derecho: totales y pago ----------------
        panel_der = ctk.CTkFrame(self, corner_radius=12)
        panel_der.grid(row=0, column=1, sticky="nsew")
        panel_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel_der, text="Resumen de venta",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

        self.label_total = ctk.CTkLabel(
            panel_der, text=f"{MONEDA}0.00",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        self.label_total.grid(row=1, column=0, sticky="w", padx=16)

        ctk.CTkLabel(panel_der, text="Forma de pago").grid(
            row=2, column=0, sticky="w", padx=16, pady=(20, 4)
        )
        self.forma_pago_var = ctk.StringVar(value="efectivo")
        frame_pago = ctk.CTkFrame(panel_der, fg_color="transparent")
        frame_pago.grid(row=3, column=0, sticky="ew", padx=16)
        for valor, etiqueta in (
            ("efectivo", "Efectivo"), ("tarjeta", "Tarjeta"), ("fiado", "Fiado"),
        ):
            ctk.CTkRadioButton(
                frame_pago, text=etiqueta, variable=self.forma_pago_var,
                value=valor, command=self._al_cambiar_forma_pago,
            ).pack(anchor="w", pady=3)

        ctk.CTkLabel(panel_der, text="Cliente (para fiado)").grid(
            row=4, column=0, sticky="w", padx=16, pady=(16, 4)
        )
        self.combo_cliente = ctk.CTkComboBox(
            panel_der, values=[], state="disabled", width=260,
        )
        self.combo_cliente.grid(row=5, column=0, sticky="ew", padx=16)
        self._cargar_clientes_combo()

        self.label_estado = ctk.CTkLabel(
            panel_der, text="", text_color="#e74c3c", wraplength=260
        )
        self.label_estado.grid(row=6, column=0, sticky="w", padx=16, pady=(10, 0))

        ctk.CTkButton(
            panel_der, text="Confirmar venta", height=48,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#27ae60", hover_color="#1e8449",
            command=self._confirmar_venta,
        ).grid(row=7, column=0, sticky="ew", padx=16, pady=(30, 16))

    # -----------------------------------------------------------------
    def _cargar_clientes_combo(self):
        self.clientes = db.listar_clientes()
        valores = [f"{c['id']} - {c['nombre']}" for c in self.clientes]
        self.combo_cliente.configure(values=valores)
        if valores:
            self.combo_cliente.set(valores[0])

    def _al_cambiar_forma_pago(self):
        if self.forma_pago_var.get() == "fiado":
            self.combo_cliente.configure(state="normal")
        else:
            self.combo_cliente.configure(state="disabled")

    # -----------------------------------------------------------------
    def _agregar_por_codigo(self):
        codigo = self.entry_codigo.get().strip()
        self.entry_codigo.delete(0, "end")
        if not codigo:
            return

        producto = db.buscar_producto_por_codigo(codigo)
        if producto is None:
            self.label_estado.configure(
                text=f"No se encontró ningún producto con el código «{codigo}».",
                text_color="#e74c3c",
            )
            return

        if producto["stock"] <= 0:
            self.label_estado.configure(
                text=f"«{producto['nombre']}» no tiene stock disponible.",
                text_color="#e67e22",
            )
            return

        # Si ya está en el carrito, solo sumamos 1
        for item in self.carrito:
            if item["producto_id"] == producto["id"]:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                self._refrescar_carrito()
                self.label_estado.configure(text="")
                return

        self.carrito.append({
            "producto_id": producto["id"],
            "nombre": producto["nombre"],
            "cantidad": 1,
            "precio_unitario": producto["precio_venta"],
            "subtotal": producto["precio_venta"],
        })
        self.label_estado.configure(text="")
        self._refrescar_carrito()

    def _cambiar_cantidad(self, delta):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            return
        indice = self.tabla_carrito.index(seleccion[0])
        item = self.carrito[indice]
        item["cantidad"] = max(1, item["cantidad"] + delta)
        item["subtotal"] = item["cantidad"] * item["precio_unitario"]
        self._refrescar_carrito()

    def _quitar_seleccionado(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            return
        indice = self.tabla_carrito.index(seleccion[0])
        self.carrito.pop(indice)
        self._refrescar_carrito()

    def _vaciar_carrito(self):
        self.carrito = []
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        for fila in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(fila)
        for item in self.carrito:
            self.tabla_carrito.insert("", "end", values=(
                item["nombre"], item["cantidad"],
                f"{MONEDA}{item['precio_unitario']:.2f}",
                f"{MONEDA}{item['subtotal']:.2f}",
            ))
        total = sum(i["subtotal"] for i in self.carrito)
        self.label_total.configure(text=f"{MONEDA}{total:,.2f}")

    # -----------------------------------------------------------------
    def _confirmar_venta(self):
        if not self.carrito:
            self.label_estado.configure(
                text="El carrito está vacío.", text_color="#e74c3c"
            )
            return

        forma_pago = self.forma_pago_var.get()
        cliente_id = None

        if forma_pago == "fiado":
            valor_combo = self.combo_cliente.get()
            if not valor_combo:
                self.label_estado.configure(
                    text="Selecciona un cliente para venta fiada.",
                    text_color="#e74c3c",
                )
                return
            cliente_id = int(valor_combo.split(" - ")[0])

        total = sum(i["subtotal"] for i in self.carrito)

        confirmar = messagebox.askyesno(
            "Confirmar venta",
            f"¿Confirmar venta por {MONEDA}{total:,.2f} ({forma_pago})?",
        )
        if not confirmar:
            return

        try:
            venta_id = db.registrar_venta(
                usuario_id=self.usuario_actual["id"],
                cliente_id=cliente_id,
                carrito=self.carrito,
                forma_pago=forma_pago,
            )
        except Exception as error:
            messagebox.showerror("Error al guardar la venta", str(error))
            return

        messagebox.showinfo(
            "Venta registrada",
            f"Venta #{venta_id} registrada correctamente.\nTotal: {MONEDA}{total:,.2f}",
        )
        self.carrito = []
        self._refrescar_carrito()
        self._cargar_clientes_combo()
        self.label_estado.configure(text="")
        self.entry_codigo.focus()
