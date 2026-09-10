"""
Pantalla de gestión de usuarios (SOLO ADMIN).

Permite:
- Ver todos los usuarios del sistema (vendedores y administradores).
- Crear un nuevo usuario con su rol.
- Activar / desactivar (bloquear) un usuario sin borrar su historial.
- Cambiar la contraseña de un usuario.

El rol "vendedor" nunca ve esta pantalla (ver main_window.py, que
filtra el menú según el rol antes de mostrar esta vista).
"""

import customtkinter as ctk
from tkinter import messagebox, ttk

from database import db


class VistaUsuarios(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        self._construir_ui()
        self._refrescar_tabla()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Gestión de usuarios (solo administrador)",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        frame_tabla = ctk.CTkFrame(self, corner_radius=12)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure(
            "Usuarios.Treeview", rowheight=28, font=("Segoe UI", 11),
            background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white",
        )
        estilo.configure("Usuarios.Treeview.Heading", font=("Segoe UI", 11, "bold"))

        columnas = ("nombre", "usuario", "rol", "estado")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", style="Usuarios.Treeview",
        )
        self.tabla.heading("nombre", text="Nombre completo")
        self.tabla.heading("usuario", text="Usuario")
        self.tabla.heading("rol", text="Rol")
        self.tabla.heading("estado", text="Estado")
        self.tabla.column("nombre", width=220)
        self.tabla.column("usuario", width=120)
        self.tabla.column("rol", width=100, anchor="center")
        self.tabla.column("estado", width=90, anchor="center")
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        ctk.CTkButton(
            frame_acciones, text="Activar/Desactivar seleccionado",
            command=self._alternar_estado,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame_acciones, text="Restablecer contraseña", command=self._restablecer_password,
        ).pack(side="left")

        # --- Panel nuevo usuario ---
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Nuevo usuario", font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        self.entry_nombre = ctk.CTkEntry(panel, placeholder_text="Nombre completo")
        self.entry_nombre.grid(row=1, column=0, sticky="ew", padx=14, pady=4)

        self.entry_usuario = ctk.CTkEntry(panel, placeholder_text="Usuario (para iniciar sesión)")
        self.entry_usuario.grid(row=2, column=0, sticky="ew", padx=14, pady=4)

        self.entry_password = ctk.CTkEntry(panel, placeholder_text="Contraseña", show="•")
        self.entry_password.grid(row=3, column=0, sticky="ew", padx=14, pady=4)

        ctk.CTkLabel(panel, text="Rol").grid(row=4, column=0, sticky="w", padx=14, pady=(10, 0))
        self.combo_rol = ctk.CTkComboBox(panel, values=["vendedor", "admin"])
        self.combo_rol.set("vendedor")
        self.combo_rol.grid(row=5, column=0, sticky="ew", padx=14, pady=4)

        ctk.CTkButton(
            panel, text="Crear usuario", command=self._crear_usuario,
        ).grid(row=6, column=0, sticky="ew", padx=14, pady=(14, 14))

        self.usuario_seleccionado_id = None

    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for usuario in db.listar_usuarios():
            self.tabla.insert(
                "", "end", iid=str(usuario["id"]),
                values=(
                    usuario["nombre_completo"],
                    usuario["usuario"],
                    usuario["rol"],
                    "Activo" if usuario["activo"] else "Bloqueado",
                ),
            )

    def _al_seleccionar(self, event=None):
        seleccion = self.tabla.selection()
        self.usuario_seleccionado_id = int(seleccion[0]) if seleccion else None

    def _crear_usuario(self):
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        rol = self.combo_rol.get()

        if not nombre or not usuario or not password:
            messagebox.showwarning("Datos incompletos", "Completa nombre, usuario y contraseña.")
            return
        if len(password) < 4:
            messagebox.showwarning("Contraseña débil", "Usa una contraseña de al menos 4 caracteres.")
            return

        try:
            db.crear_usuario(nombre, usuario, password, rol)
        except Exception as error:
            messagebox.showerror(
                "No se pudo crear el usuario",
                f"Es posible que el usuario «{usuario}» ya exista.\n\nDetalle: {error}",
            )
            return

        messagebox.showinfo("Usuario creado", f"«{usuario}» fue creado con rol {rol}.")
        for entry in (self.entry_nombre, self.entry_usuario, self.entry_password):
            entry.delete(0, "end")
        self._refrescar_tabla()

    def _alternar_estado(self):
        if self.usuario_seleccionado_id is None:
            messagebox.showwarning("Selecciona un usuario", "Elige un usuario de la tabla.")
            return
        if self.usuario_seleccionado_id == self.usuario_actual["id"]:
            messagebox.showwarning("Acción no permitida", "No puedes bloquear tu propio usuario.")
            return

        usuarios = {u["id"]: u for u in db.listar_usuarios()}
        usuario = usuarios.get(self.usuario_seleccionado_id)
        nuevo_estado = not bool(usuario["activo"])
        db.cambiar_estado_usuario(self.usuario_seleccionado_id, nuevo_estado)
        self._refrescar_tabla()

    def _restablecer_password(self):
        if self.usuario_seleccionado_id is None:
            messagebox.showwarning("Selecciona un usuario", "Elige un usuario de la tabla.")
            return

        dialogo = ctk.CTkInputDialog(
            text="Nueva contraseña para este usuario:", title="Restablecer contraseña",
        )
        nueva_password = dialogo.get_input()
        if not nueva_password:
            return
        if len(nueva_password) < 4:
            messagebox.showwarning("Contraseña débil", "Usa al menos 4 caracteres.")
            return

        db.cambiar_password_usuario(self.usuario_seleccionado_id, nueva_password)
        messagebox.showinfo("Listo", "La contraseña fue actualizada.")
