"""
Ventana principal de la aplicación (después del login).

Tiene un menú lateral (sidebar) que cambia de pantalla dentro del
mismo panel de contenido. Las opciones que se muestran dependen
del ROL del usuario que inició sesión:

- Vendedor: Venta, Clientes/Fiado, Cierre de caja.
- Admin: todo lo anterior + Reportes + Usuarios.

Esto cumple el requisito de permisos: un vendedor JAMÁS ve el
botón de Reportes ni el de Usuarios, porque ni siquiera se
construyen esos botones para su rol.
"""

import customtkinter as ctk
from tkinter import messagebox

from config import NOMBRE_APP, VERSION_APP
from ui.venta_view import VistaVenta
from ui.clientes_view import VistaClientes
from ui.caja_view import VistaCaja
from ui.reportes_view import VistaReportes
from ui.usuarios_view import VistaUsuarios


class VentanaPrincipal(ctk.CTk):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual  # sqlite3.Row con id, nombre_completo, rol, etc.
        self.vista_actual = None

        self.title(f"{NOMBRE_APP} — {usuario_actual['nombre_completo']} ({usuario_actual['rol']})")
        self.geometry("1180x720")
        self.minsize(980, 620)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_area_contenido()

        # Pantalla inicial: venta
        self._mostrar_venta()

    # -----------------------------------------------------------------
    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text=f"🔧 {NOMBRE_APP}",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=190, justify="left",
        ).pack(padx=16, pady=(20, 4), anchor="w")

        ctk.CTkLabel(
            sidebar,
            text=f"{self.usuario_actual['nombre_completo']}\nRol: {self.usuario_actual['rol'].capitalize()}",
            font=ctk.CTkFont(size=11), text_color="gray", justify="left",
        ).pack(padx=16, pady=(0, 20), anchor="w")

        self.botones_menu = []

        def agregar_boton(texto, comando):
            boton = ctk.CTkButton(
                sidebar, text=texto, anchor="w", height=42,
                fg_color="transparent", command=comando,
            )
            boton.pack(fill="x", padx=12, pady=3)
            self.botones_menu.append(boton)
            return boton

        # --- Opciones disponibles para TODOS los roles ---
        agregar_boton("🛒  Venta", self._mostrar_venta)
        agregar_boton("👥  Clientes / Fiado", self._mostrar_clientes)
        agregar_boton("🧾  Cierre de caja", self._mostrar_caja)

        # --- Opciones SOLO ADMIN ---
        if self.usuario_actual["rol"] == "admin":
            agregar_boton("📊  Reportes", self._mostrar_reportes)
            agregar_boton("🔑  Usuarios", self._mostrar_usuarios)

        # Espaciador + cerrar sesión al fondo
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(expand=True, fill="both")

        ctk.CTkButton(
            sidebar, text="Cerrar sesión", fg_color="#c0392b",
            hover_color="#922b21", command=self._cerrar_sesion,
        ).pack(fill="x", padx=12, pady=(4, 6))

        ctk.CTkLabel(
            sidebar, text=f"v{VERSION_APP}", font=ctk.CTkFont(size=10), text_color="gray",
        ).pack(pady=(0, 12))

    def _construir_area_contenido(self):
        self.area_contenido = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.area_contenido.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.area_contenido.grid_rowconfigure(0, weight=1)
        self.area_contenido.grid_columnconfigure(0, weight=1)

    def _cambiar_vista(self, clase_vista, *args):
        if self.vista_actual is not None:
            self.vista_actual.destroy()
        self.vista_actual = clase_vista(self.area_contenido, *args)
        self.vista_actual.grid(row=0, column=0, sticky="nsew")

    # -----------------------------------------------------------------
    def _mostrar_venta(self):
        self._cambiar_vista(VistaVenta, self.usuario_actual)

    def _mostrar_clientes(self):
        self._cambiar_vista(VistaClientes, self.usuario_actual)

    def _mostrar_caja(self):
        self._cambiar_vista(VistaCaja, self.usuario_actual)

    def _mostrar_reportes(self):
        if self.usuario_actual["rol"] != "admin":
            messagebox.showerror("Acceso denegado", "Solo un administrador puede ver reportes.")
            return
        self._cambiar_vista(VistaReportes, self.usuario_actual)

    def _mostrar_usuarios(self):
        if self.usuario_actual["rol"] != "admin":
            messagebox.showerror("Acceso denegado", "Solo un administrador puede gestionar usuarios.")
            return
        self._cambiar_vista(VistaUsuarios, self.usuario_actual)

    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar la sesión actual?")
        if not confirmar:
            return
        self.destroy()

        # Reinicia el flujo completo: vuelve a mostrar el login
        from ui.login_window import VentanaLogin
        login = VentanaLogin()
        login.mainloop()
        if login.usuario_autenticado is not None:
            nueva_ventana = VentanaPrincipal(login.usuario_autenticado)
            nueva_ventana.mainloop()
