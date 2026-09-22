"""Modelo Pago: pagos asociados a membresías (Pagado / Pendiente)."""
from datetime import date

from data.database import conexion


class Pago:
    """Pago asociado a una membresía, con monto, fecha y estado."""

    ESTADOS = ("Pagado", "Pendiente")

    def __init__(self, id_pago=None, id_membresia=None, monto=0.0,
                 fecha_pago=None, estado="Pendiente",
                 cliente_nombre=None, cliente_apellido=None, tipo_membresia=None):
        """Crea un pago y normaliza sus valores mediante las propiedades."""
        self._id_pago = id_pago
        self.id_membresia = id_membresia
        self.monto = monto
        self._fecha_pago = self._a_fecha(fecha_pago or date.today().isoformat())
        self.estado = estado
        self._cliente_nombre = cliente_nombre
        self._cliente_apellido = cliente_apellido
        self._tipo_membresia = tipo_membresia

    # --- Propiedades ---

    @property
    def id_pago(self):
        return self._id_pago

    @property
    def id_membresia(self):
        return self._id_membresia

    @id_membresia.setter
    def id_membresia(self, valor):
        try:
            self._id_membresia = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Debe seleccionar una membresía.")

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError("El monto debe ser un número.")
        if valor < 0:
            raise ValueError("El monto no puede ser negativo.")
        self._monto = valor

    @property
    def fecha_pago(self):
        return self._fecha_pago

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        valor = str(valor or "").strip()
        if valor not in self.ESTADOS:
            raise ValueError("El estado debe ser 'Pagado' o 'Pendiente'.")
        self._estado = valor

    @property
    def cliente_nombre(self):
        return self._cliente_nombre or ""

    @property
    def cliente_apellido(self):
        return self._cliente_apellido or ""

    @property
    def tipo_membresia(self):
        return self._tipo_membresia or ""

    def nombre_cliente(self):
        return f"{self._cliente_nombre} {self._cliente_apellido}".strip() or f"Cliente de membresía #{self._id_membresia}"

    def __str__(self):
        return f"Pago #{self._id_pago or 'nuevo'} ({self._estado})"

    # --- Persistencia ---

    def guardar(self):
        with conexion() as conn:
            if self._id_pago is None:
                cursor = conn.execute(
                    """INSERT INTO pago (id_membresia, monto, fecha_pago, estado)
                       VALUES (?, ?, ?, ?)""",
                    (self._id_membresia, self._monto,
                     self._fecha_pago.isoformat(), self._estado),
                )
                self._id_pago = cursor.lastrowid
            else:
                conn.execute(
                    """UPDATE pago
                       SET id_membresia = ?, monto = ?, fecha_pago = ?, estado = ?
                       WHERE id_pago = ?""",
                    (self._id_membresia, self._monto,
                     self._fecha_pago.isoformat(), self._estado, self._id_pago),
                )
        return self._id_pago

    def eliminar(self):
        """Elimina el pago indicado por su identificador."""
        if self._id_pago is None:
            return
        with conexion() as conn:
            conn.execute("DELETE FROM pago WHERE id_pago = ?", (self._id_pago,))
        self._id_pago = None

    # --- Listados ---

    @staticmethod
    def _a_fecha(valor):
        """Convierte una fecha ISO en ``date`` y valida su formato."""
        if isinstance(valor, date):
            return valor
        try:
            return date.fromisoformat(str(valor).strip())
        except ValueError:
            raise ValueError("Las fechas deben tener formato YYYY-MM-DD.")

    @classmethod
    def _desde_fila(cls, fila):
        """Convierte una fila con JOIN de membresía y cliente en un pago."""
        return cls(
            id_pago=fila["id_pago"],
            id_membresia=fila["id_membresia"],
            monto=fila["monto"],
            fecha_pago=fila["fecha_pago"],
            estado=fila["estado"],
            cliente_nombre=fila["cliente_nombre"],
            cliente_apellido=fila["cliente_apellido"],
            tipo_membresia=fila["tipo_membresia"],
        )

    @staticmethod
    def _consulta_base():
        """Devuelve el JOIN común usado por las consultas de pagos."""
        return (
            "SELECT p.*, m.tipo AS tipo_membresia, "
            "c.nombre AS cliente_nombre, c.apellido AS cliente_apellido "
            "FROM pago p "
            "JOIN membresia m ON m.id_membresia = p.id_membresia "
            "JOIN cliente c ON c.id_cliente = m.id_cliente"
        )

    @classmethod
    def listar_todas(cls):
        """Obtiene todos los pagos enriquecidos con datos relacionados."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " ORDER BY p.fecha_pago DESC, c.apellido"
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_por_membresia(cls, id_membresia):
        """Obtiene los pagos asociados a una membresía."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " WHERE p.id_membresia = ? ORDER BY p.fecha_pago DESC",
                (id_membresia,),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        """Obtiene los pagos históricos de un cliente."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " WHERE m.id_cliente = ? ORDER BY p.fecha_pago DESC",
                (id_cliente,),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @staticmethod
    def clientes_con_pagos_pendientes():
        """JOIN pago + membresia + cliente para el reporte de cartera."""
        with conexion() as conn:
            filas = conn.execute(
                """SELECT p.id_pago, p.monto, p.fecha_pago, p.estado,
                          m.id_membresia, m.tipo,
                          c.id_cliente, c.nombre, c.apellido, c.documento
                   FROM pago p
                   JOIN membresia m ON m.id_membresia = p.id_membresia
                   JOIN cliente c ON c.id_cliente = m.id_cliente
                   WHERE p.estado = 'Pendiente'
                   ORDER BY c.apellido, c.nombre"""
            ).fetchall()
        return [dict(f) for f in filas]