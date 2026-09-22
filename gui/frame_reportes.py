"""Reportes: vencimientos próximos, pagos pendientes e historial de clientes."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from controllers.reporte_controller import ReporteController


class FrameReportes(tk.Frame):
    """Vista de consultas agregadas sobre vencimientos, pagos e historial."""

    def __init__(self, master, controller=None):
        """Construye las pestañas y recibe el controlador de reportes."""
        super().__init__(master, padx=12, pady=12)
        self.controller = controller or ReporteController()
        self._construir_tabs()

    def _construir_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._construir_tab_vencimientos()
        self._construir_tab_pagos()
        self._construir_tab_historial()

    def refrescar(self):
        """Actualiza los reportes que no requieren seleccionar un cliente."""
        self._consultar_vencimientos()
        self._consultar_pagos()

    # ---- Pestaña 1: Membresías próximas a vencer ----

    def _construir_tab_vencimientos(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Vencimientos Próximos")

        controles = ttk.Frame(frame)
        controles.pack(fill="x", pady=(0, 8))
        ttk.Label(controles, text="Membresías que vencen en los próximos").pack(side="left")
        self.var_dias = tk.StringVar(value="30")
        ttk.Spinbox(controles, from_=1, to=365, width=6,
                     textvariable=self.var_dias).pack(side="left", padx=6)
        ttk.Label(controles, text="días").pack(side="left")
        ttk.Button(controles, text="Consultar",
                   command=self._consultar_vencimientos).pack(side="left", padx=(16, 0))

        cols = ("id", "cliente", "tipo", "inicio", "vencimiento", "dias", "valor")
        self.tree_vencimientos = self._crear_tabla(frame, cols)
        self.columnas_venc = cols

    def _consultar_vencimientos(self):
        """Consulta membresías vencidas o próximas a vencer."""
        try:
            dias = int(self.var_dias.get())
            if dias <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor inválido", "Ingrese un número de días válido.", parent=self)
            return
        membresias = self.controller.membresias_por_vencer(dias)
        hoy = date.today()
        datos = []
        for m in membresias:
            delta = (m.fecha_vencimiento - hoy).days
            datos.append((
                m.id_membresia,
                m.nombre_cliente(),
                m.tipo,
                m.fecha_inicio.isoformat(),
                m.fecha_vencimiento.isoformat(),
                f"{delta} días" if delta >= 0 else f"Venció hace {abs(delta)} días",
                f"${m.valor:,}",
            ))
        self._llenar_tree(self.tree_vencimientos, self.columnas_venc, datos)

    # ---- Pestaña 2: Pagos pendientes ----

    def _construir_tab_pagos(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Pagos Pendientes")

        ttk.Label(frame, text="Clientes con pagos pendientes:").pack(anchor="w", pady=(0, 6))
        cols = ("id_pago", "cliente", "documento", "tipo", "monto", "fecha", "membresia")
        self.tree_pagos = self._crear_tabla(frame, cols)
        self.columnas_pagos = cols

    def _consultar_pagos(self):
        """Consulta y muestra los pagos pendientes de los clientes."""
        datos = self.controller.pagos_pendientes()
        filas = [
            (
                f["id_pago"],
                f"{f['nombre']} {f['apellido']}",
                f["documento"],
                f["tipo"],
                f"${f['monto']:,.0f}",
                f["fecha_pago"],
                f"Memb. #{f['id_membresia']}",
            )
            for f in datos
        ]
        self._llenar_tree(self.tree_pagos, self.columnas_pagos, filas)

    # ---- Pestaña 3: Historial de cliente ----

    def _construir_tab_historial(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Historial de Cliente")

        barra = ttk.Frame(frame)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Seleccionar cliente:").pack(side="left")
        self.var_cliente_hist = tk.StringVar()
        self.combo_cliente = ttk.Combobox(barra, textvariable=self.var_cliente_hist,
                                          state="readonly", width=42)
        self.combo_cliente.pack(side="left", padx=6)
        ttk.Button(barra, text="Consultar",
                   command=self._consultar_historial).pack(side="left", padx=(8, 0))

        sep1 = ttk.Label(frame, text="Membresías", font=("Segoe UI", 10, "bold"))
        sep1.pack(anchor="w", pady=(8, 2))
        cols_mem = ("id", "tipo", "inicio", "vencimiento", "estado", "valor")
        self.tree_hist_mem = self._crear_tabla(frame, cols_mem, height=5)
        self.columnas_hist_mem = cols_mem

        sep2 = ttk.Label(frame, text="Pagos", font=("Segoe UI", 10, "bold"))
        sep2.pack(anchor="w", pady=(8, 2))
        cols_pag = ("id", "fecha", "monto", "estado")
        self.tree_hist_pag = self._crear_tabla(frame, cols_pag, height=5)
        self.columnas_hist_pag = cols_pag

        sep3 = ttk.Label(frame, text="Planes de Entrenamiento", font=("Segoe UI", 10, "bold"))
        sep3.pack(anchor="w", pady=(8, 2))
        cols_plan = ("id", "nombre", "nivel", "duracion", "entrenador")
        self.tree_hist_plan = self._crear_tabla(frame, cols_plan, height=5)
        self.columnas_hist_plan = cols_plan

    def _cargar_clientes_historial(self):
        """Carga clientes en el selector de la pestaña de historial."""
        clientes = self.controller.listar_clientes()
        opciones = [f"{c.id_cliente} | {c.apellido}, {c.nombre}" for c in clientes]
        self.combo_cliente.configure(values=opciones)
        return opciones

    def _consultar_historial(self):
        """Muestra membresías, pagos y planes del cliente seleccionado."""
        etiqueta = self.var_cliente_hist.get()
        if not etiqueta:
            messagebox.showinfo("Historial", "Seleccione un cliente.", parent=self)
            return
        id_cliente = int(etiqueta.split(" | ")[0])

        historial = self.controller.historial_cliente(id_cliente)
        membresias = historial["membresias"]
        self._llenar_tree(self.tree_hist_mem, self.columnas_hist_mem, [
            (
                m.id_membresia,
                m.tipo,
                m.fecha_inicio.isoformat(),
                m.fecha_vencimiento.isoformat(),
                m.estado,
                f"${m.valor:,}",
            )
            for m in membresias
        ])

        pagos = historial["pagos"]
        self._llenar_tree(self.tree_hist_pag, self.columnas_hist_pag, [
            (
                p.id_pago,
                p.fecha_pago.isoformat(),
                f"${p.monto:,.0f}",
                p.estado,
            )
            for p in pagos
        ])

        planes = historial["planes"]
        self._llenar_tree(self.tree_hist_plan, self.columnas_hist_plan, [
            (
                p.id_plan,
                p.nombre,
                p.nivel,
                f"{p.duracion_semanas} sem.",
                p.entrenador_nombre_completo(),
            )
            for p in planes
        ])

    # ---- Utilidades internas ----

    @staticmethod
    def _crear_tabla(frame, columnas, height=10):
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, pady=(0, 4))

        tree = ttk.Treeview(tree_frame, columns=columnas, show="headings",
                            selectmode="browse")
        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        return tree

    @staticmethod
    def _llenar_tree(tree, columnas, filas):
        tree.delete(*tree.get_children())
        for fila in filas:
            tree.insert("", "end", values=fila)
        if not filas:
            tree.insert("", "end", values=["Sin registros"])