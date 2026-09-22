"""Módulo de pagos: registro de pagos y control de pendientes."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from models.membresia import Membresia
from models.pago import Pago


class FramePagos(tk.Frame):
    COLUMNAS = ("id_pago", "id_membresia", "cliente", "tipo",
                "fecha_pago", "monto", "estado")

    def __init__(self, master):
        super().__init__(master, padx=12, pady=12)
        self._id_actual = None
        self._datos = []
        self._opciones_membresias = []
        self._construir_busqueda()
        self._construir_tabla()
        self._construir_formulario()
        self._cargar_membresias()
        self.refrescar()

    # --- UI ---

    def _construir_busqueda(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Filtrar por cliente:").pack(side="left")
        self.var_busqueda = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_busqueda, width=30).pack(side="left", padx=6)
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
            "id_pago": ("ID Pago", 60, tk.CENTER),
            "id_membresia": ("Memb.", 60, tk.CENTER),
            "cliente": ("Cliente", 180, tk.W),
            "tipo": ("Tipo", 100, tk.CENTER),
            "fecha_pago": ("Fecha", 100, tk.CENTER),
            "monto": ("Monto", 100, tk.CENTER),
            "estado": ("Estado", 90, tk.CENTER),
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
        form = ttk.LabelFrame(self, text="Formulario de pago", padding=10)
        form.pack(fill="x", pady=(10, 0))

        self.var_membresia = tk.StringVar()
        self.var_monto = tk.StringVar()
        self.var_fecha_pago = tk.StringVar(value=date.today().isoformat())
        self.var_estado = tk.StringVar(value="Pendiente")

        ttk.Label(form, text="Membresía *").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.combo_membresia = ttk.Combobox(form, textvariable=self.var_membresia,
                                            state="readonly", width=45)
        self.combo_membresia.grid(row=0, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Monto *").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_monto, width=14).grid(
            row=0, column=3, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Fecha (YYYY-MM-DD)").grid(
            row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(form, textvariable=self.var_fecha_pago, width=30).grid(
            row=1, column=1, sticky="w", padx=(0, 24), pady=4)

        ttk.Label(form, text="Estado *").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=4)
        self.combo_estado = ttk.Combobox(form, textvariable=self.var_estado,
                                         values=list(Pago.ESTADOS),
                                         state="readonly", width=14)
        self.combo_estado.grid(row=1, column=3, sticky="w", pady=4)

        botones = ttk.Frame(form)
        botones.grid(row=0, column=4, rowspan=2, sticky="n", padx=(10, 0))
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Editar", command=self._editar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(fill="x", pady=2)

        form.columnconfigure(4, weight=1)

    # --- Datos ---

    def _cargar_membresias(self):
        self._opciones_membresias = []
        for m in Membresia.listar_todas():
            etiqueta = f"{m.id_membresia} | {m.nombre_cliente()} - {m.tipo}"
            self._opciones_membresias.append(etiqueta)
        self.combo_membresia.configure(values=self._opciones_membresias)

    def _id_membresia_seleccionada(self):
        etiqueta = self.var_membresia.get()
        if not etiqueta:
            raise ValueError("Debe seleccionar una membresía.")
        return int(etiqueta.split(" | ")[0])

    def refrescar(self):
        self._cargar_membresias()
        pagos = Pago.listar_todas()
        self._datos = [
            {
                "id_pago": str(p.id_pago),
                "id_membresia": str(p.id_membresia),
                "cliente": p.nombre_cliente(),
                "tipo": p.tipo_membresia,
                "fecha_pago": p.fecha_pago.isoformat(),
                "monto": f"${p.monto:,.0f}",
                "estado": p.estado,
            }
            for p in pagos
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
            pago = Pago(
                id_pago=self._id_actual,
                id_membresia=self._id_membresia_seleccionada(),
                monto=self.var_monto.get(),
                fecha_pago=self.var_fecha_pago.get(),
                estado=self.var_estado.get(),
            )
            pago.guardar()
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e), parent=self)
            return
        messagebox.showinfo("Pagos", "Pago guardado correctamente.", parent=self)
        self._limpiar()
        self.refrescar()

    def _editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Editar", "Seleccione un pago de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        self._id_actual = int(valores["id_pago"])
        self.var_membresia.set(self._membresia_por_id(valores["id_membresia"], valores["cliente"],
                                                      valores["tipo"]))
        self.var_monto.set(str(int(valores["monto"].replace("$", "").replace(",", ""))))
        self.var_fecha_pago.set(valores["fecha_pago"])
        self.var_estado.set(valores["estado"])

    def _membresia_por_id(self, id_membresia, cliente, tipo):
        objetivo = f"{id_membresia} | "
        for etiqueta in self._opciones_membresias:
            if etiqueta.startswith(objetivo):
                return etiqueta
        return f"{id_membresia} | {cliente} - {tipo}"

    def _eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Seleccione un pago de la tabla.", parent=self)
            return
        valores = dict(zip(self.COLUMNAS, self.tabla.item(seleccion[0])["values"]))
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar el pago #{valores['id_pago']} de "
                                   f"'{valores['cliente']}'?", parent=self):
            return
        pago = Pago(id_pago=int(valores["id_pago"]))
        pago.eliminar()
        self._limpiar()
        self.refrescar()

    def _limpiar(self):
        self._id_actual = None
        self.var_membresia.set("")
        self.var_monto.set("")
        self.var_fecha_pago.set(date.today().isoformat())
        self.var_estado.set("Pendiente")
        self.tabla.selection_remove(*self.tabla.selection())