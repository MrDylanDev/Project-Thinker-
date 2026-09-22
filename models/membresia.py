"""Modelo Membresía: estado dinámico, vencimientos y renovaciones."""
from datetime import date, timedelta

from data.database import conexion

PLANES_DURACION = {
    "Mensual": 30,
    "Trimestral": 90,
    "Semestral": 180,
    "Anual": 365,
}

PLANES_VALOR = {
    "Mensual": 30000,
    "Trimestral": 84000,
    "Semestral": 156000,
    "Anual": 288000,
}


class Membresia:
    """Membresía de un cliente con fechas, valor y estado calculado."""

    def __init__(self, id_membresia=None, id_cliente=None, tipo="Mensual",
                 fecha_inicio=None, fecha_vencimiento=None, estado="Activa",
                 cliente_nombre=None, cliente_apellido=None):
        """Crea una membresía y calcula su vencimiento si no fue proporcionado."""
        self._id_membresia = id_membresia
        self.id_cliente = id_cliente
        self.tipo = tipo
        self._fecha_inicio = self._a_fecha(fecha_inicio or date.today().isoformat())
        if fecha_vencimiento:
            self._fecha_vencimiento = self._a_fecha(fecha_vencimiento)
        else:
            self._fecha_vencimiento = self._fecha_inicio + timedelta(
                days=PLANES_DURACION[self._tipo]
            )
        self._estado = estado
        self._cliente_nombre = cliente_nombre
        self._cliente_apellido = cliente_apellido

    # --- Propiedades ---

    @property
    def id_membresia(self):
        return self._id_membresia

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        try:
            self._id_cliente = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Debe seleccionar un cliente.")

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        valor = str(valor or "").strip()
        if valor not in PLANES_DURACION:
            raise ValueError("El tipo de membresía es inválido.")
        self._tipo = valor

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def fecha_vencimiento(self):
        return self._fecha_vencimiento

    @property
    def valor(self):
        return PLANES_VALOR[self._tipo]

    @property
    def estado(self):
        """Recalculado dinámicamente: Cancelada > Vencida > Activa."""
        if self._estado == "Cancelada":
            return "Cancelada"
        if self._fecha_vencimiento < date.today():
            return "Vencida"
        return "Activa"

    @property
    def estado_registrado(self):
        """Estado persistido tal cual ('Activa' o 'Cancelada')."""
        return self._estado

    @property
    def cliente_nombre(self):
        return self._cliente_nombre or ""

    @property
    def cliente_apellido(self):
        return self._cliente_apellido or ""

    def nombre_cliente(self):
        return f"{self._cliente_nombre} {self._cliente_apellido}".strip() or f"Cliente #{self._id_cliente}"

    def __str__(self):
        return f"Membresía {self._tipo} #{self._id_membresia or 'nueva'}"

    # --- Persistencia ---

    def guardar(self):
        """Inserta o actualiza. El vencimiento nace de 'fecha_inicio + duración'
        sólo al crear o si cambian tipo/fecha de inicio en una edición."""
        with conexion() as conn:
            if self._id_membresia is None:
                vencimiento = self._fecha_inicio + timedelta(days=PLANES_DURACION[self._tipo])
                cursor = conn.execute(
                    """INSERT INTO membresia (id_cliente, tipo, fecha_inicio,
                                              fecha_vencimiento, estado)
                       VALUES (?, ?, ?, ?, ?)""",
                    (self._id_cliente, self._tipo, self._fecha_inicio.isoformat(),
                     vencimiento.isoformat(), self._estado),
                )
                self._id_membresia = cursor.lastrowid
                self._fecha_vencimiento = vencimiento
            else:
                fila = conn.execute(
                    """SELECT tipo, fecha_inicio, fecha_vencimiento
                       FROM membresia WHERE id_membresia = ?""",
                    (self._id_membresia,),
                ).fetchone()
                if fila is None:
                    raise ValueError("La membresía ya no existe en la base de datos.")
                if fila["tipo"] != self._tipo or fila["fecha_inicio"] != self._fecha_inicio.isoformat():
                    self._fecha_vencimiento = self._fecha_inicio + timedelta(
                        days=PLANES_DURACION[self._tipo]
                    )
                conn.execute(
                    """UPDATE membresia
                       SET id_cliente = ?, tipo = ?, fecha_inicio = ?,
                           fecha_vencimiento = ?, estado = ?
                       WHERE id_membresia = ?""",
                    (self._id_cliente, self._tipo, self._fecha_inicio.isoformat(),
                     self._fecha_vencimiento.isoformat(), self._estado,
                     self._id_membresia),
                )
        return self._id_membresia

    def renovar(self):
        """Extiende el vencimiento según el tipo; revierte cancelaciones."""
        if self._estado != "Cancelada":
            base = max(date.today(), self._fecha_vencimiento)
        else:
            base = date.today()
        self._fecha_vencimiento = base + timedelta(days=PLANES_DURACION[self._tipo])
        self._estado = "Activa"
        self.guardar()

    def cancelar(self):
        """Marca la membresía como cancelada."""
        self._estado = "Cancelada"
        self.guardar()

    def eliminar(self):
        """Elimina la membresía y los pagos dependientes por clave foránea."""
        if self._id_membresia is None:
            return
        with conexion() as conn:
            conn.execute(
                "DELETE FROM membresia WHERE id_membresia = ?", (self._id_membresia,)
            )
        self._id_membresia = None

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
        """Convierte una fila con JOIN de cliente en una membresía."""
        return cls(
            id_membresia=fila["id_membresia"],
            id_cliente=fila["id_cliente"],
            tipo=fila["tipo"],
            fecha_inicio=fila["fecha_inicio"],
            fecha_vencimiento=fila["fecha_vencimiento"],
            estado=fila["estado"],
            cliente_nombre=fila["cliente_nombre"],
            cliente_apellido=fila["cliente_apellido"],
        )

    @staticmethod
    def _consulta_base():
        return (
            "SELECT m.*, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido "
            "FROM membresia m JOIN cliente c ON c.id_cliente = m.id_cliente"
        )

    @classmethod
    def listar_todas(cls):
        """Obtiene todas las membresías junto con el nombre del cliente."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " ORDER BY m.fecha_vencimiento, c.apellido"
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        """Obtiene las membresías históricas de un cliente."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " WHERE m.id_cliente = ? ORDER BY m.fecha_vencimiento DESC",
                (id_cliente,),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_proximas_a_vencer(cls, dias):
        """Membresías activas (no canceladas) cuyo vencimiento cae en N días."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + """
                WHERE m.estado != 'Cancelada'
                  AND m.fecha_vencimiento >= date('now')
                  AND m.fecha_vencimiento <= date('now', '+' || ? || ' days')
                ORDER BY m.fecha_vencimiento""",
                (int(dias),),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_vencidas(cls):
        """Obtiene membresías vencidas que no fueron canceladas."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + """
                WHERE m.estado != 'Cancelada' AND m.fecha_vencimiento < date('now')
                ORDER BY m.fecha_vencimiento"""
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]