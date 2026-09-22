"""Módulo de entrenadores: tabla de listado + formulario de alta/edición."""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from controllers.entrenador_controller import EntrenadorController


class FrameEntrenadores(tk.Frame):
    """Vista Tkinter para administrar entrenadores del gimnasio."""

    COLUMNAS = ("id", "nombre", "apellido", "especialidad", "telefono", "email")

    def __init__(self, master, controller=None):
        """Construye la vista y recibe su controlador mediante inyección."""
        super().__init__(master, padx=12, pady=12)
        self.controller = controller or EntrenadorController()
        self._id_actual = None
        self._datos = []
        self._construir_busqueda()
        self._construir_tabla()
        self._construir_formulario()
        self.refrescar()

    # --- UI ---

    def _construir_busqueda(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Buscar entrenador:").pack(side="left")
        self.var_busqueda = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_busqueda, width=30).pack(side="left", padx=6)
        ttk.Button(barra, text="Buscar", command=self._buscar).pack(side="left", padx=(0, 6))
        ttk.Button(barra, text="Mostrar todos",
                   command=lambda: (self.var_busqueda.set(""), self.refrescar())).pack(side="left")

    def _construir_tabla(self):
        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        self.tabla = ttk.Treeview(contenedor, columns=self.COLUMNAS, show="headings",
                                  selectmode="browse")
        encabezados = {
            "id": ("ID", 40, tk.CENTER),
            "nombre": ("Nombre", 150, tk.W),
            "apellido": ("Apellido", 150, tk.W),
            "especialidad": ("Especialidad", 180, tk.W),
            "telefono": ("Teléfono", 110, tk.CENTER),
            "email": ("Email", 200, tk.W),
        }
        for col in self.COLUMNAS:
            texto, ancho, ancla = encabezados[col]
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=ancla)

        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    def _construir_formulario(self):
        form = ttk.LabelFrame(self, text="Formulario de entrenador", padding=10)
        form.pack(fill="x", pady=(10, 0))

        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_especialidad = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_email = tk.StringVar()

        campos = [
            (0, 0, "Nombre *", self.var_nombre),
            (0, 2, "Apellido *", self.var_apellido),
            (1, 0, "Especialidad", self.var_especialidad),
            (1, 2, "Teléfono", self.var_telefono),
            (2, 0, "Email", self.var_email),
        ]
        for fila, col, etiqueta, var in campos:
            ttk.Label(form, text=etiqueta).grid(row=fila, column=col, sticky="w", padx=(0, 6), pady=4)
            ttk.Entry(form, textvariable=var, width=30).grid(row=fila, column=col + 1, sticky="w", padx=(0, 24), pady=4)

        botones = ttk.Frame(form)
        botones.grid(row=0, column=4, rowspan=3, sticky="n", padx=(10, 0))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Editar", command=self._editar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(fill="x", pady=2)

        form.columnconfigure(4, weight=1)

    # --- Datos ---

    def refrescar(self):
        """Obtiene entrenadores del controlador y actualiza la tabla."""
        entrenadores = self.controller.listar()
        self._datos = [
            {
                "id": str(e.id_entrenador),
                "nombre": e.nombre,
                "apellido": e.apellido,
                "especialidad": e.especialidad,
                "telefono": e.telefono,
                "email": e.email,
            }
            for e in entrenadores
        ]
        self._llenar_tabla()

    def _buscar(self):
        """Filtra la tabla por nombre, apellido o especialidad."""
        texto = self.var_busqueda.get().strip()
        if not texto:
            self.refrescar()
            return
        entrenadores = self.controller.buscar(texto)
        self._datos = [
            {
                "id": str(e.id_entrenador),
                "nombre": e.nombre,
                "apellido": e.apellido,
                "especialidad": e.especialidad,
                "telefono": e.telefono,
                "email": e.email,
            }
            for e in entrenadores
        ]
        self._llenar_tabla()

    def _llenar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for fila in self._datos:
            self.tabla.insert("", "end", values=tuple(fila.get(c, "") for c in self.COLUMNAS))

    # --- Acciones ---

    def _guardar(self):
        """Valida y delega al controlador la creación o edición."""
        try:
            self.controller.guardar(
                self._id_actual, self.var_nombre.get(), self.var_apellido.get(),
                self.var_especialidad.get(), self.var_telefono.get(), self.var_email.get(),
            )
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e), parent=self)
            return
        messagebox.showinfo("Entrenadores", "Entrenador guardado correctamente.", parent=self)
        self._limpiar()
        self.refrescar()

    def _editar(self):
        """Carga en el formulario los datos del entrenador seleccionado."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Editar", "Seleccione un entrenador de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        self._id_actual = int(valores["id"])
        self.var_nombre.set(valores["nombre"])
        self.var_apellido.set(valores["apellido"])
        self.var_especialidad.set(valores["especialidad"])
        self.var_telefono.set(valores["telefono"])
        self.var_email.set(valores["email"])

    def _eliminar(self):
        """Confirma y delega al controlador la eliminación."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccione un entrenador de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar al entrenador '{valores['nombre']} {valores['apellido']}'?",
                                   parent=self):
            return
        try:
            self.controller.eliminar(int(valores["id"]))
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}", parent=self)
            return
        self._limpiar()
        self.refrescar()

    def _limpiar(self):
        """Restablece el formulario y la selección actual."""
        self._id_actual = None
        for var in (self.var_nombre, self.var_apellido, self.var_especialidad,
                    self.var_telefono, self.var_email):
            var.set("")
        self.tabla.selection_remove(*self.tabla.selection())