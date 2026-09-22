"""Ventana principal: menú lateral que alterna entre los módulos."""
import tkinter as tk
from tkinter import ttk

from data.database import inicializar_base_datos
from .frame_clientes import FrameClientes
from .frame_entrenadores import FrameEntrenadores
from .frame_membresias import FrameMembresias
from .frame_pagos import FramePagos
from .frame_planes import FramePlanes
from .frame_reportes import FrameReportes


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gimnasio Fitness Plus")
        self.geometry("1150x720")
        self.minsize(960, 620)

        inicializar_base_datos()

        self._frames = {}
        self._frame_actual = None
        self._construir_ui()
        self._mostrar_frame(FrameClientes)

    def _construir_ui(self):
        lateral = ttk.Frame(self, padding=(10, 12))
        lateral.pack(side="left", fill="y")

        titulo = ttk.Label(lateral, text="Fitness Plus",
                           font=("Segoe UI", 14, "bold"))
        titulo.pack(anchor="w", pady=(0, 16))
        subtitulo = ttk.Label(lateral, text="Sistema de gestión",
                              font=("Segoe UI", 9))
        subtitulo.pack(anchor="w", pady=(0, 16))

        self._titulo_modulo = ttk.Label(self, text="", font=("Segoe UI", 14, "bold"))
        self._titulo_modulo.pack(side="top", anchor="w", padx=12, pady=(8, 0))

        self._contenedor = ttk.Frame(self)
        self._contenedor.pack(side="top", fill="both", expand=True)

        modulos = [
            ("Clientes", FrameClientes),
            ("Entrenadores", FrameEntrenadores),
            ("Membresías", FrameMembresias),
            ("Pagos", FramePagos),
            ("Planes", FramePlanes),
            ("Reportes", FrameReportes),
        ]
        for texto, clase in modulos:
            boton = ttk.Button(lateral, text=texto, width=16,
                               command=lambda c=clase, t=texto: self._mostrar_frame(c, t))
            boton.pack(fill="x", pady=3)

    def _mostrar_frame(self, clase, titulo=None):
        if self._frame_actual is not None:
            self._frame_actual.pack_forget()
        if clase not in self._frames:
            self._frames[clase] = clase(self._contenedor)
        self._frame_actual = self._frames[clase]
        self._frame_actual.refrescar()
        self._frame_actual.pack(fill="both", expand=True)
        if titulo:
            self._titulo_modulo.configure(text=titulo)