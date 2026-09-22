"""Punto de entrada: Gimnasio Fitness Plus."""
from gui.ventana_principal import VentanaPrincipal

if __name__ == "__main__":
    """Construye la ventana principal y ejecuta el bucle de eventos Tkinter."""
    app = VentanaPrincipal()
    app.mainloop()