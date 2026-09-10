"""
Pantalla de reportes (SOLO ADMIN).

Muestra:
- Producto más vendido del día.
- Top 5 productos del día por unidades vendidas.
- Ventas totales del día.
- Clientes con deuda pendiente (fiado).

También incluye el botón de respaldo manual de la base de datos
("Respaldar ahora"), ya que gestionar respaldos es una tarea
administrativa.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import os

from database import db
from backup import backup_manager
from config import MONEDA, BACKUP_DIR, BACKUP_MAX_COPIAS


class VistaReportes(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        self._construir_ui()
        self._refrescar()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="Reportes del día (solo administrador)",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # --- Tarjeta: producto más vendido ---
        tarjeta_top = ctk.CTkFrame(self, corner_radius=14)
        tarjeta_top.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 12))
        ctk.CTkLabel(
            tarjeta_top, text="⭐ Producto más vendido hoy",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))
        self.label_top_producto = ctk.CTkLabel(
            tarjeta_top, text="Sin ventas todavía", font=ctk.CTkFont(size=16),
        )
        self.label_top_producto.pack(anchor="w", padx=16, pady=(0, 14))

        # --- Tarjeta: total del día ---
        tarjeta_total = ctk.CTkFrame(self, corner_radius=14)
        tarjeta_total.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 12))
        ctk.CTkLabel(
            tarjeta_total, text="💰 Ventas totales hoy",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))
        self.label_total_dia = ctk.CTkLabel(
            tarjeta_total, text=f"{MONEDA}0.00",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.label_total_dia.pack(anchor="w", padx=16, pady=(0, 14))

        # --- Top 5 productos ---
        frame_top5 = ctk.CTkFrame(self, corner_radius=12)
        frame_top5.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        frame_top5.grid_rowconfigure(1, weight=1)
        frame_top5.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_top5, text="Top 5 productos del día",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Reportes.Treeview", rowheight=26, font=("Segoe UI", 10),
            background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white",
        )
        estilo.configure("Reportes.Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tabla_top5 = ttk.Treeview(
            frame_top5, columns=("producto", "unidades", "vendido"),
            show="headings", style="Reportes.Treeview",
        )
        self.tabla_top5.heading("producto", text="Producto")
        self.tabla_top5.heading("unidades", text="Unidades")
        self.tabla_top5.heading("vendido", text="Total vendido")
        self.tabla_top5.column("producto", width=200)
        self.tabla_top5.column("unidades", width=80, anchor="center")
        self.tabla_top5.column("vendido", width=100, anchor="e")
        self.tabla_top5.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # --- Clientes con deuda ---
        frame_deudas = ctk.CTkFrame(self, corner_radius=12)
        frame_deudas.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        frame_deudas.grid_rowconfigure(1, weight=1)
        frame_deudas.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_deudas, text="Clientes con deuda pendiente",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self.tabla_deudas = ttk.Treeview(
            frame_deudas, columns=("cliente", "saldo"),
            show="headings", style="Reportes.Treeview",
        )
        self.tabla_deudas.heading("cliente", text="Cliente")
        self.tabla_deudas.heading("saldo", text="Saldo")
        self.tabla_deudas.column("cliente", width=220)
        self.tabla_deudas.column("saldo", width=100, anchor="e")
        self.tabla_deudas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # --- Respaldo ---
        frame_backup = ctk.CTkFrame(self, corner_radius=12)
        frame_backup.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        ctk.CTkLabel(
            frame_backup, text="Respaldo en la nube",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left", padx=14, pady=12)

        self.label_backup_info = ctk.CTkLabel(
            frame_backup, text="", text_color="gray",
        )
        self.label_backup_info.pack(side="left", padx=8)

        ctk.CTkButton(
            frame_backup, text="Respaldar ahora", command=self._respaldar_ahora,
        ).pack(side="right", padx=14, pady=12)

        ctk.CTkButton(
            frame_backup, text="Actualizar reportes", command=self._refrescar,
            fg_color="transparent", border_width=1,
        ).pack(side="right", padx=6, pady=12)

    def _refrescar(self):
        top = db.producto_mas_vendido_del_dia()
        if top:
            nombre, cantidad = top
            self.label_top_producto.configure(text=f"{nombre}  ({cantidad} unidades)")
        else:
            self.label_top_producto.configure(text="Sin ventas todavía")

        resumen = db.resumen_caja_del_dia()
        self.label_total_dia.configure(text=f"{MONEDA}{resumen['total_general']:,.2f}")

        for fila in self.tabla_top5.get_children():
            self.tabla_top5.delete(fila)
        for prod in db.top_productos_del_dia():
            self.tabla_top5.insert("", "end", values=(
                prod["nombre_producto"], prod["total_unidades"],
                f"{MONEDA}{prod['total_vendido']:.2f}",
            ))

        for fila in self.tabla_deudas.get_children():
            self.tabla_deudas.delete(fila)
        for cliente in db.clientes_con_deuda():
            self.tabla_deudas.insert("", "end", values=(
                cliente["nombre"], f"{MONEDA}{cliente['saldo_deuda']:.2f}",
            ))

        cantidad_respaldos = len(backup_manager.listar_respaldos())
        self.label_backup_info.configure(
            text=f"Carpeta: {BACKUP_DIR}\n{cantidad_respaldos} respaldo(s) guardado(s) (máx. {BACKUP_MAX_COPIAS})"
        )

    def _respaldar_ahora(self):
        try:
            ruta = backup_manager.hacer_respaldo()
        except Exception as error:
            messagebox.showerror("Error al respaldar", str(error))
            return
        messagebox.showinfo(
            "Respaldo creado",
            f"Se guardó un respaldo en:\n{ruta}",
        )
        self._refrescar()
