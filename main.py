"""
Punto de entrada de POS Ferretería PRO.

Ejecutar con:

    python main.py

Flujo:
1. Se inicializa la base de datos (crea tablas y siembra datos de
   ejemplo la primera vez que se ejecuta).
2. Se muestra la ventana de login.
3. Si el login es exitoso, se abre la ventana principal con el
   menú correspondiente al rol del usuario (admin / vendedor).
"""

import customtkinter as ctk

from config import TEMA, COLOR_TEMA
from database.db import inicializar_base_datos
from ui.login_window import VentanaLogin
from ui.main_window import VentanaPrincipal


def main():
    ctk.set_appearance_mode(TEMA)
    ctk.set_default_color_theme(COLOR_TEMA)

    inicializar_base_datos()

    login = VentanaLogin()
    login.mainloop()

    if login.usuario_autenticado is not None:
        ventana_principal = VentanaPrincipal(login.usuario_autenticado)
        ventana_principal.mainloop()


if __name__ == "__main__":
    main()
