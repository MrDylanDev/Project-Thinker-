"""Módulo de planes de entrenamiento: vincula cliente con entrenador."""
import tkinter as tk
from tkinter import ttk, messagebox

from controllers.plan_controller import PlanController, NIVELES


class FramePlanes(tk.Frame):
    """Vista para vincular clientes con entrenadores mediante planes."""

    COLUMNAS = ("id_plan", "nombre", "nivel", "duracion", "descripcion",
                "entrenador", "cliente")

    def __init__(self, master, controller=None):
        """Construye la vista e inyecta el controlador de planes."""
        super().__init__(master, padx=12, pady=12)
        self.controller = controller or PlanController()
        self._id_actual = None
        self._datos = []
        self._opciones_clientes = []
        self._opciones_entrenadores = []
        self._construir_busqueda()
        self._construir_tabla()
        self._construir_formulario()
        self._cargar_opciones()
        self.refrescar()

    # --- UI ---

    def _construir_busqueda(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Filtrar por cliente o entrenador:").pack(side="left")
        self.var_busqueda = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_busqueda, width=34).pack(side="left", padx=6)
        ttk.Button(barra, text="Filtrar", command=self._buscar).pack(side="left", padx=(0, 6))
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
            "id_plan": ("ID", 40, tk.CENTER),
            "nombre": ("Nombre", 150, tk.W),
            "nivel": ("Nivel", 110, tk.CENTER),
            "duracion": ("Duración", 80, tk.CENTER),
            "descripcion": ("Descripción", 220, tk.W),
            "entrenador": ("Entrenador", 160, tk.W),
            "cliente": ("Cliente", 160, tk.W),
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
        form = ttk.LabelFrame(self, text="Formulario de plan de entrenamiento", padding=10)
        form.pack(fill="x", pady=(10, 0))

        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_nivel = tk.StringVar(value="Principiante")
        self.var_duracion = tk.StringVar(value="4")
        self.var_entrenador = tk.StringVar()
        self.var_cliente = tk.StringVar()

        ttk.Label(form, text="Nombre *").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_nombre, width=28).grid(
            row=0, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Entrenador *").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=4)
        self.combo_entrenador = ttk.Combobox(form, textvariable=self.var_entrenador,
                                             state="readonly", width=32)
        self.combo_entrenador.grid(row=0, column=3, sticky="w", padx=(0, 12), pady=4)

        ttk.Label(form, text="Nivel *").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_nivel = ttk.Combobox(form, textvariable=self.var_nivel,
                                        values=list(NIVELES), state="readonly", width=16)
        self.combo_nivel.grid(row=1, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Duración (semanas) *").grid(
            row=1, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_duracion, width=12).grid(
            row=1, column=3, sticky="w", padx=(0, 12), pady=4)

        ttk.Label(form, text="Cliente *").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_cliente = ttk.Combobox(form, textvariable=self.var_cliente,
                                          state="readonly", width=32)
        self.combo_cliente.grid(row=2, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Descripción").grid(row=2, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_descripcion, width=36).grid(
            row=2, column=3, sticky="w", padx=(0, 12), pady=4)

        botones = ttk.Frame(form)
        botones.grid(row=0, column=4, rowspan=3, sticky="n", padx=(10, 0))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Editar", command=self._editar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(fill="x", pady=2)

        form.columnconfigure(4, weight=1)

    # --- Datos ---

    def _cargar_opciones(self):
        """Carga clientes y entrenadores en los selectores del formulario."""
        self._opciones_clientes = []
        for c in self.controller.listar_clientes():
            etiqueta = f"{c.id_cliente} | {c.apellido}, {c.nombre}"
            self._opciones_clientes.append(etiqueta)
        self.combo_cliente.configure(values=self._opciones_clientes)

        self._opciones_entrenadores = []
        for e in self.controller.listar_entrenadores():
            etiqueta = f"{e.id_entrenador} | {e.apellido}, {e.nombre}"
            self._opciones_entrenadores.append(etiqueta)
        self.combo_entrenador.configure(values=self._opciones_entrenadores)

    def _id_desde_etiqueta(self, etiqueta):
        """Convierte una opción con formato ``id | descripción`` en un entero."""
        if not etiqueta:
            raise ValueError("Debe completar la selección.")
        return int(etiqueta.split(" | ")[0])

    def refrescar(self):
        """Recarga opciones y planes visibles en la tabla."""
        self._cargar_opciones()
        planes = self.controller.listar()
        self._datos = [
            {
                "id_plan": str(p.id_plan),
                "nombre": p.nombre,
                "nivel": p.nivel,
                "duracion": f"{p.duracion_semanas} sem.",
                "descripcion": p.descripcion,
                "entrenador": p.entrenador_nombre_completo(),
                "cliente": p.cliente_nombre_completo(),
            }
            for p in planes
        ]
        self._llenar_tabla()

    def _buscar(self):
        texto = self.var_busqueda.get().strip().lower()
        if not texto:
            self.refrescar()
            return
        self._datos = [
            f for f in self._datos
            if texto in f["cliente"].lower() or texto in f["entrenador"].lower()
        ]
        self._llenar_tabla()

    def _llenar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for fila in self._datos:
            self.tabla.insert("", "end", values=tuple(fila.get(c, "") for c in self.COLUMNAS))

    # --- Acciones ---

    def _guardar(self):
        """Crea o actualiza un plan mediante el controlador."""
        try:
            self.controller.guardar(
                self._id_actual, self.var_nombre.get(), self.var_descripcion.get(),
                self.var_nivel.get(), self.var_duracion.get(),
                self._id_desde_etiqueta(self.var_entrenador.get()),
                self._id_desde_etiqueta(self.var_cliente.get()),
            )
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e), parent=self)
            return
        messagebox.showinfo("Planes", "Plan de entrenamiento guardado.", parent=self)
        self._limpiar()
        self.refrescar()

    def _editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Editar", "Seleccione un plan de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        self._id_actual = int(valores["id_plan"])
        self.var_nombre.set(valores["nombre"])
        self.var_descripcion.set(valores["descripcion"])
        self.var_nivel.set(valores["nivel"])
        self.var_duracion.set(valores["duracion"].replace(" sem.", ""))
        self.var_entrenador.set(self._entrenador_segun_nombre(valores["entrenador"]))
        self.var_cliente.set(self._cliente_segun_nombre(valores["cliente"]))

    def _entrenador_segun_nombre(self, nombre):
        for etiqueta in self._opciones_entrenadores:
            if etiqueta.split(" | ")[1] == nombre:
                return etiqueta
        return nombre

    def _cliente_segun_nombre(self, nombre):
        for etiqueta in self._opciones_clientes:
            if etiqueta.split(" | ")[1] == nombre:
                return etiqueta
        return nombre

    def _eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccione un plan de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar el plan '{valores['nombre']}'?", parent=self):
            return
        self.controller.eliminar(int(valores["id_plan"]))
        self._limpiar()
        self.refrescar()

    def _limpiar(self):
        """Restablece el formulario y la selección de la tabla."""
        self._id_actual = None
        for var in (self.var_nombre, self.var_descripcion, self.var_entrenador,
                    self.var_cliente):
            var.set("")
        self.var_nivel.set("Principiante")
        self.var_duracion.set("4")
        self.tabla.selection_remove(*self.tabla.selection())