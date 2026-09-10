"""
Pantalla de cierre de caja.

Muestra el resumen de ventas del día (efectivo, tarjeta, fiado y
total general) y permite hacer el "cierre de caja" formal, que
guarda una foto de ese resumen en la tabla cierres_caja para
tener historial.

Disponible para admin y vendedor (el vendedor normalmente es
quien cierra su turno).
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import datetime

from database import db
from config import MONEDA


class VistaCaja(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        self._construir_ui()
        self._refrescar()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            self, text=f"Cierre de caja — {datetime.date.today().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 16))

        self.tarjetas = {}
        etiquetas = [
            ("efectivo", "Efectivo", "#27ae60"),
            ("tarjeta", "Tarjeta", "#2980b9"),
            ("fiado", "Fiado", "#e67e22"),
            ("total_general", "Total general", "#8e44ad"),
        ]
        for i, (clave, titulo, color) in enumerate(etiquetas):
            tarjeta = ctk.CTkFrame(self, corner_radius=14, fg_color=color)
            tarjeta.grid(row=1, column=i, sticky="nsew", padx=6, pady=6)
            ctk.CTkLabel(
                tarjeta, text=titulo, font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
            ).pack(pady=(16, 4))
            valor_label = ctk.CTkLabel(
                tarjeta, text=f"{MONEDA}0.00",
                font=ctk.CTkFont(size=24, weight="bold"), text_color="white",
            )
            valor_label.pack(pady=(0, 16))
            self.tarjetas[clave] = valor_label

        self.label_cantidad_ventas = ctk.CTkLabel(
            self, text="0 ventas registradas hoy", font=ctk.CTkFont(size=13),
        )
        self.label_cantidad_ventas.grid(row=2, column=0, columnspan=4, sticky="w", pady=(14, 0))

        # Tabla de ventas del día
        frame_tabla = ctk.CTkFrame(self, corner_radius=12)
        frame_tabla.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(14, 14))
        self.grid_rowconfigure(3, weight=1)
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Caja.Treeview", rowheight=26, font=("Segoe UI", 10),
            background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white",
        )
        estilo.configure("Caja.Treeview.Heading", font=("Segoe UI", 10, "bold"))

        columnas = ("hora", "vendedor", "cliente", "forma_pago", "total")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", style="Caja.Treeview",
        )
        for col, titulo, ancho in [
            ("hora", "Hora", 90), ("vendedor", "Vendedor", 150),
            ("cliente", "Cliente", 150), ("forma_pago", "Forma de pago", 100),
            ("total", "Total", 90),
        ]:
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="w" if col != "total" else "e")
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.grid(row=4, column=0, columnspan=4, sticky="ew")

        ctk.CTkButton(
            frame_botones, text="Actualizar", width=120, command=self._refrescar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame_botones, text="Hacer cierre de caja", width=180,
            fg_color="#8e44ad", hover_color="#6c3483",
            command=self._hacer_cierre,
        ).pack(side="left")

    def _refrescar(self):
        resumen = db.resumen_caja_del_dia()
        self.tarjetas["efectivo"].configure(text=f"{MONEDA}{resumen['efectivo']:,.2f}")
        self.tarjetas["tarjeta"].configure(text=f"{MONEDA}{resumen['tarjeta']:,.2f}")
        self.tarjetas["fiado"].configure(text=f"{MONEDA}{resumen['fiado']:,.2f}")
        self.tarjetas["total_general"].configure(text=f"{MONEDA}{resumen['total_general']:,.2f}")
        self.label_cantidad_ventas.configure(
            text=f"{resumen['cantidad_ventas']} ventas registradas hoy"
        )

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for venta in db.ventas_del_dia():
            hora = venta["fecha"].split("T")[1] if "T" in venta["fecha"] else venta["fecha"]
            self.tabla.insert("", "end", values=(
                hora,
                venta["vendedor"] or "-",
                venta["cliente"] or "Mostrador",
                venta["forma_pago"].capitalize(),
                f"{MONEDA}{venta['total']:.2f}",
            ))

    def _hacer_cierre(self):
        confirmar = messagebox.askyesno(
            "Confirmar cierre de caja",
            "¿Deseas guardar el cierre de caja del día con los datos actuales?",
        )
        if not confirmar:
            return
        resumen = db.guardar_cierre_caja(self.usuario_actual["id"])
        messagebox.showinfo(
            "Cierre guardado",
            "Cierre de caja registrado.\n\n"
            f"Efectivo: {MONEDA}{resumen['efectivo']:,.2f}\n"
            f"Tarjeta: {MONEDA}{resumen['tarjeta']:,.2f}\n"
            f"Fiado: {MONEDA}{resumen['fiado']:,.2f}\n"
            f"Total: {MONEDA}{resumen['total_general']:,.2f}",
        )
        self._refrescar()
