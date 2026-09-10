"""
Pantalla de clientes / fiado.

Permite:
- Ver la lista de clientes con su saldo de deuda actual.
- Registrar un cliente nuevo.
- Registrar un abono (pago) a la deuda de un cliente.

Disponible tanto para admin como para vendedor, porque en una
ferretería normalmente el vendedor es quien recibe los abonos
de los clientes fiado.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk

from database import db
from config import MONEDA


class VistaClientes(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        self._construir_ui()
        self._refrescar_tabla()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Clientes y cuentas por cobrar (fiado)",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # --- Tabla de clientes ---
        frame_tabla = ctk.CTkFrame(self, corner_radius=12)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Clientes.Treeview", rowheight=28, font=("Segoe UI", 11),
            background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white",
        )
        estilo.configure("Clientes.Treeview.Heading", font=("Segoe UI", 11, "bold"))

        columnas = ("nombre", "telefono", "limite", "deuda")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings",
            style="Clientes.Treeview",
        )
        self.tabla.heading("nombre", text="Cliente")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("limite", text="Límite crédito")
        self.tabla.heading("deuda", text="Saldo actual")
        self.tabla.column("nombre", width=240)
        self.tabla.column("telefono", width=120)
        self.tabla.column("limite", width=110, anchor="e")
        self.tabla.column("deuda", width=110, anchor="e")
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        # --- Panel derecho: nuevo cliente / abono ---
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Nuevo cliente", font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        self.entry_nombre = ctk.CTkEntry(panel, placeholder_text="Nombre completo")
        self.entry_nombre.grid(row=1, column=0, sticky="ew", padx=14, pady=4)
        self.entry_telefono = ctk.CTkEntry(panel, placeholder_text="Teléfono")
        self.entry_telefono.grid(row=2, column=0, sticky="ew", padx=14, pady=4)
        self.entry_direccion = ctk.CTkEntry(panel, placeholder_text="Dirección")
        self.entry_direccion.grid(row=3, column=0, sticky="ew", padx=14, pady=4)
        self.entry_limite = ctk.CTkEntry(panel, placeholder_text="Límite de crédito")
        self.entry_limite.grid(row=4, column=0, sticky="ew", padx=14, pady=4)

        ctk.CTkButton(
            panel, text="Guardar cliente", command=self._guardar_cliente,
        ).grid(row=5, column=0, sticky="ew", padx=14, pady=(8, 20))

        ctk.CTkLabel(
            panel, text="Registrar abono a deuda",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=6, column=0, sticky="w", padx=14, pady=(0, 6))

        self.label_cliente_sel = ctk.CTkLabel(
            panel, text="Selecciona un cliente en la tabla →", text_color="gray",
            wraplength=200,
        )
        self.label_cliente_sel.grid(row=7, column=0, sticky="w", padx=14)

        self.entry_abono = ctk.CTkEntry(panel, placeholder_text="Monto a abonar")
        self.entry_abono.grid(row=8, column=0, sticky="ew", padx=14, pady=(10, 4))

        ctk.CTkButton(
            panel, text="Registrar abono", fg_color="#27ae60",
            hover_color="#1e8449", command=self._registrar_abono,
        ).grid(row=9, column=0, sticky="ew", padx=14, pady=(4, 14))

        self.cliente_seleccionado_id = None

    # -----------------------------------------------------------------
    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for cliente in db.listar_clientes():
            self.tabla.insert(
                "", "end", iid=str(cliente["id"]),
                values=(
                    cliente["nombre"],
                    cliente["telefono"] or "-",
                    f"{MONEDA}{cliente['limite_credito']:.2f}",
                    f"{MONEDA}{cliente['saldo_deuda']:.2f}",
                ),
            )

    def _al_seleccionar(self, event=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.cliente_seleccionado_id = None
            self.label_cliente_sel.configure(text="Selecciona un cliente en la tabla →")
            return
        self.cliente_seleccionado_id = int(seleccion[0])
        cliente = db.obtener_cliente(self.cliente_seleccionado_id)
        self.label_cliente_sel.configure(
            text=f"{cliente['nombre']}\nDeuda actual: {MONEDA}{cliente['saldo_deuda']:.2f}"
        )

    def _guardar_cliente(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        direccion = self.entry_direccion.get().strip()
        limite_texto = self.entry_limite.get().strip() or "0"

        if not nombre:
            messagebox.showwarning("Falta información", "El nombre del cliente es obligatorio.")
            return
        try:
            limite = float(limite_texto)
        except ValueError:
            messagebox.showwarning("Dato inválido", "El límite de crédito debe ser un número.")
            return

        db.crear_cliente(nombre, telefono, direccion, limite)
        messagebox.showinfo("Cliente registrado", f"«{nombre}» fue agregado correctamente.")

        for entry in (self.entry_nombre, self.entry_telefono, self.entry_direccion, self.entry_limite):
            entry.delete(0, "end")

        self._refrescar_tabla()

    def _registrar_abono(self):
        if self.cliente_seleccionado_id is None:
            messagebox.showwarning("Selecciona un cliente", "Elige un cliente de la tabla primero.")
            return

        monto_texto = self.entry_abono.get().strip()
        try:
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Monto inválido", "Ingresa un monto positivo válido.")
            return

        db.registrar_abono_deuda(
            self.cliente_seleccionado_id, self.usuario_actual["id"], monto
        )
        messagebox.showinfo("Abono registrado", f"Se registró un abono de {MONEDA}{monto:.2f}.")
        self.entry_abono.delete(0, "end")
        self._refrescar_tabla()
        self._al_seleccionar()
