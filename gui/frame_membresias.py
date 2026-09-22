"""Módulo de membresías: alta/edición, renovación y cancelación."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from models.cliente import Cliente
from models.membresia import Membresia, PLANES_DURACION, PLANES_VALOR


class FrameMembresias(tk.Frame):
    COLUMNAS = ("id_membresia", "cliente", "tipo", "fecha_inicio",
                "fecha_vencimiento", "estado", "valor")

    def __init__(self, master):
        super().__init__(master, padx=12, pady=12)
        self._id_actual = None
        self._estado_original = None
        self._datos = []
        self._opciones_clientes = []
        self._construir_busqueda()
        self._construir_tabla()
        self._construir_formulario()
        self._cargar_clientes()
        self.refrescar()

    # --- UI ---

    def _construir_busqueda(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Filtrar por cliente:").pack(side="left")
        self.var_busqueda = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_busqueda, width=30).pack(side="left", padx=6)
        ttk.Button(barra, text="Filtrar", command=self._buscar).pack(side="left", padx=(0, 6))
        ttk.Button(barra, text="Mostrar todas",
                   command=lambda: (self.var_busqueda.set(""), self.refrescar())).pack(side="left")

    def _construir_tabla(self):
        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        self.tabla = ttk.Treeview(contenedor, columns=self.COLUMNAS, show="headings",
                                  selectmode="browse")
        encabezados = {
            "id_membresia": ("ID", 40, tk.CENTER),
            "cliente": ("Cliente", 180, tk.W),
            "tipo": ("Tipo", 100, tk.CENTER),
            "fecha_inicio": ("Inicio", 100, tk.CENTER),
            "fecha_vencimiento": ("Vence", 100, tk.CENTER),
            "estado": ("Estado", 90, tk.CENTER),
            "valor": ("Valor", 90, tk.CENTER),
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
        form = ttk.LabelFrame(self, text="Formulario de membresía", padding=10)
        form.pack(fill="x", pady=(10, 0))

        self.var_cliente = tk.StringVar()
        self.var_tipo = tk.StringVar(value="Mensual")
        self.var_fecha_inicio = tk.StringVar(value=date.today().isoformat())

        ttk.Label(form, text="Cliente *").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_cliente = ttk.Combobox(form, textvariable=self.var_cliente,
                                          state="readonly", width=40)
        self.combo_cliente.grid(row=0, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Tipo *").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=4)
        self.combo_tipo = ttk.Combobox(form, textvariable=self.var_tipo,
                                       values=list(PLANES_DURACION.keys()),
                                       state="readonly", width=16)
        self.combo_tipo.grid(row=0, column=3, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Fecha de inicio (YYYY-MM-DD)").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_fecha_inicio, width=30).grid(
            row=1, column=1, sticky="w", padx=(0, 24), pady=4)

        self.var_info = tk.StringVar(
            value="Valor y vencimiento automáticos: "
                  + "; ".join(f"{t} = ${v:,}"
                              for t, v in PLANES_VALOR.items()))
        ttk.Label(form, textvariable=self.var_info).grid(
            row=1, column=2, columnspan=2, sticky="w", pady=4)

        botones = ttk.Frame(form)
        botones.grid(row=0, column=4, rowspan=2, sticky="n", padx=(10, 0))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Editar", command=self._editar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Renovar", command=self._renovar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Cancelar", command=self._cancelar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(fill="x", pady=2)

        form.columnconfigure(4, weight=1)

    # --- Datos ---

    def _cargar_clientes(self):
        self._opciones_clientes = []
        for c in Cliente.listar_todos():
            etiqueta = f"{c.id_cliente} | {c.apellido}, {c.nombre}"
            self._opciones_clientes.append(etiqueta)
        self.combo_cliente.configure(values=self._opciones_clientes)

    def _id_cliente_seleccionado(self):
        etiqueta = self.var_cliente.get()
        if not etiqueta:
            raise ValueError("Debe seleccionar un cliente.")
        return int(etiqueta.split(" | ")[0])

    def refrescar(self):
        self._cargar_clientes()
        membresias = Membresia.listar_todas()
        self._datos = [
            {
                "id_membresia": str(m.id_membresia),
                "cliente": m.nombre_cliente(),
                "tipo": m.tipo,
                "fecha_inicio": m.fecha_inicio.isoformat(),
                "fecha_vencimiento": m.fecha_vencimiento.isoformat(),
                "estado": m.estado,
                "valor": f"${m.valor:,}",
                "_estado_bd": m.estado_registrado,
            }
            for m in membresias
        ]
        self._llenar_tabla()

    def _buscar(self):
        texto = self.var_busqueda.get().strip().lower()
        if not texto:
            self.refrescar()
            return
        self._datos = [f for f in self._datos if texto in f["cliente"].lower()]
        self._llenar_tabla()

    def _llenar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for fila in self._datos:
            self.tabla.insert("", "end", values=tuple(fila.get(c, "") for c in self.COLUMNAS))

    # --- Acciones ---

    def _guardar(self):
        try:
            membresia = Membresia(
                id_membresia=self._id_actual,
                id_cliente=self._id_cliente_seleccionado(),
                tipo=self.var_tipo.get(),
                fecha_inicio=self.var_fecha_inicio.get(),
                estado=self._estado_original or "Activa",
            )
            membresia.guardar()
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e), parent=self)
            return
        messagebox.showinfo("Membresías", "Membresía guardada correctamente.", parent=self)
        self._limpiar()
        self.refrescar()

    def _editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Editar", "Seleccione una membresía de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        fila = next((f for f in self._datos if f["id_membresia"] == valores["id_membresia"]), None)
        self._id_actual = int(valores["id_membresia"])
        self._estado_original = fila["_estado_bd"] if fila else "Activa"
        self.var_cliente.set(valores["cliente"])
        self._ajustar_cliente_segun_nombre(valores["cliente"])
        self.var_tipo.set(valores["tipo"])
        self.var_fecha_inicio.set(valores["fecha_inicio"])

    def _ajustar_cliente_segun_nombre(self, nombre_cliente):
        for etiqueta in self._opciones_clientes:
            if etiqueta.split(" | ")[1] == nombre_cliente:
                self.var_cliente.set(etiqueta)
                return

    def _renovar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Renovar", "Seleccione una membresía de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Renovar",
                                   f"¿Renovar la membresía #{valores['id_membresia']} "
                                   f"({valores['tipo']}) del cliente '{valores['cliente']}'?",
                                   parent=self):
            return
        try:
            membresia = Membresia(id_membresia=int(valores["id_membresia"]))
            membresia.renovar()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        messagebox.showinfo("Membresías", "Membresía renovada correctamente.", parent=self)
        self._limpiar()
        self.refrescar()

    def _cancelar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Cancelar", "Seleccione una membresía de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Cancelar",
                                   f"¿Cancelar la membresía #{valores['id_membresia']} "
                                   f"del cliente '{valores['cliente']}'?",
                                   parent=self):
            return
        membresia = Membresia(id_membresia=int(valores["id_membresia"]))
        membresia.cancelar()
        messagebox.showinfo("Membresías", "Membresía cancelada.", parent=self)
        self._limpiar()
        self.refrescar()

    def _eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccione una membresía de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar la membresía #{valores['id_membresia']}?",
                                   parent=self):
            return
        membresia = Membresia(id_membresia=int(valores["id_membresia"]))
        membresia.eliminar()
        self._limpiar()
        self.refrescar()

    def _limpiar(self):
        self._id_actual = None
        self._estado_original = None
        self.var_cliente.set("")
        self.var_tipo.set("Mensual")
        self.var_fecha_inicio.set(date.today().isoformat())
        self.tabla.selection_remove(*self.tabla.selection())