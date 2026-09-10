"""
Ventana de inicio de sesión.

Pide usuario y contraseña, valida contra la base de datos
(usuarios.py / db.py) y, si son correctos, cierra esta ventana
y abre la ventana principal (main_window.py) con el usuario
autenticado.
"""

import customtkinter as ctk
from tkinter import messagebox

from database import db
from config import NOMBRE_APP, VERSION_APP


class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{NOMBRE_APP} - Iniciar sesión")
        self.geometry("420x480")
        self.resizable(False, False)

        # Centrar contenido
        contenedor = ctk.CTkFrame(self, corner_radius=16)
        contenedor.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(
            contenedor, text="🔧", font=ctk.CTkFont(size=48)
        ).pack(pady=(30, 0))

        ctk.CTkLabel(
            contenedor, text=NOMBRE_APP,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(5, 0))

        ctk.CTkLabel(
            contenedor, text="Sistema de punto de venta multiusuario",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(pady=(0, 25))

        self.entry_usuario = ctk.CTkEntry(
            contenedor, placeholder_text="Usuario", width=260, height=38
        )
        self.entry_usuario.pack(pady=8)
        self.entry_usuario.focus()

        self.entry_password = ctk.CTkEntry(
            contenedor, placeholder_text="Contraseña", show="•",
            width=260, height=38,
        )
        self.entry_password.pack(pady=8)
        self.entry_password.bind("<Return>", lambda e: self._intentar_login())

        self.label_error = ctk.CTkLabel(
            contenedor, text="", text_color="#e74c3c", font=ctk.CTkFont(size=12)
        )
        self.label_error.pack(pady=(4, 0))

        ctk.CTkButton(
            contenedor, text="Ingresar", width=260, height=38,
            command=self._intentar_login,
        ).pack(pady=(18, 6))

        ctk.CTkLabel(
            contenedor,
            text="Demo → admin / admin123  ·  vendedor / vendedor123",
            font=ctk.CTkFont(size=10), text_color="gray",
        ).pack(pady=(20, 0))

        ctk.CTkLabel(
            contenedor, text=f"v{VERSION_APP}",
            font=ctk.CTkFont(size=10), text_color="gray",
        ).pack(side="bottom", pady=10)

        self.usuario_autenticado = None

    def _intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            self.label_error.configure(text="Ingresa usuario y contraseña.")
            return

        fila_usuario = db.autenticar_usuario(usuario, password)

        if fila_usuario is None:
            self.label_error.configure(text="Usuario o contraseña incorrectos.")
            self.entry_password.delete(0, "end")
            return

        self.usuario_autenticado = fila_usuario
        self.destroy()
