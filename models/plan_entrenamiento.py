"""Modelo PlanEntrenamiento: vincula un cliente con un entrenador."""
from data.database import conexion

NIVELES = ("Principiante", "Intermedio", "Avanzado")


class PlanEntrenamiento:
    def __init__(self, id_plan=None, nombre="", descripcion="", nivel="Principiante",
                 duracion_semanas=4, id_entrenador=None, id_cliente=None,
                 nombre_entrenador=None, apellido_entrenador=None,
                 nombre_cliente=None, apellido_cliente=None):
        self._id_plan = id_plan
        self.nombre = nombre
        self.descripcion = descripcion
        self.nivel = nivel
        self.duracion_semanas = duracion_semanas
        self.id_entrenador = id_entrenador
        self.id_cliente = id_cliente
        self._nombre_entrenador = nombre_entrenador
        self._apellido_entrenador = apellido_entrenador
        self._nombre_cliente = nombre_cliente
        self._apellido_cliente = apellido_cliente

    # --- Propiedades ---

    @property
    def id_plan(self):
        return self._id_plan

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor or "").strip()
        if not valor:
            raise ValueError("El nombre del plan no puede estar vacío.")
        self._nombre = valor

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        self._descripcion = str(valor or "").strip()

    @property
    def nivel(self):
        return self._nivel

    @nivel.setter
    def nivel(self, valor):
        valor = str(valor or "").strip()
        if valor not in NIVELES:
            raise ValueError("El nivel debe ser Principiante, Intermedio o Avanzado.")
        self._nivel = valor

    @property
    def duracion_semanas(self):
        return self._duracion_semanas

    @duracion_semanas.setter
    def duracion_semanas(self, valor):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ValueError("La duración debe ser un número entero de semanas.")
        if valor <= 0:
            raise ValueError("La duración debe ser mayor que cero.")
        self._duracion_semanas = valor

    @property
    def id_entrenador(self):
        return self._id_entrenador

    @id_entrenador.setter
    def id_entrenador(self, valor):
        try:
            self._id_entrenador = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Debe seleccionar un entrenador.")

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
    def nombre_entrenador(self):
        return self._nombre_entrenador or ""

    @property
    def apellido_entrenador(self):
        return self._apellido_entrenador or ""

    @property
    def nombre_cliente(self):
        return self._nombre_cliente or ""

    @property
    def apellido_cliente(self):
        return self._apellido_cliente or ""

    def entrenador_nombre_completo(self):
        return f"{self._nombre_entrenador} {self._apellido_entrenador}".strip() or f"Entrenador #{self._id_entrenador}"

    def cliente_nombre_completo(self):
        return f"{self._nombre_cliente} {self._apellido_cliente}".strip() or f"Cliente #{self._id_cliente}"

    def __str__(self):
        return f"Plan '{self._nombre}' ({self._nivel})"

    # --- Persistencia ---

    def guardar(self):
        with conexion() as conn:
            if self._id_plan is None:
                cursor = conn.execute(
                    """INSERT INTO plan_entrenamiento
                       (nombre, descripcion, nivel, duracion_semanas,
                        id_entrenador, id_cliente)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (self._nombre, self._descripcion, self._nivel,
                     self._duracion_semanas, self._id_entrenador, self._id_cliente),
                )
                self._id_plan = cursor.lastrowid
            else:
                conn.execute(
                    """UPDATE plan_entrenamiento
                       SET nombre = ?, descripcion = ?, nivel = ?,
                           duracion_semanas = ?, id_entrenador = ?, id_cliente = ?
                       WHERE id_plan = ?""",
                    (self._nombre, self._descripcion, self._nivel,
                     self._duracion_semanas, self._id_entrenador, self._id_cliente,
                     self._id_plan),
                )
        return self._id_plan

    def eliminar(self):
        if self._id_plan is None:
            return
        with conexion() as conn:
            conn.execute(
                "DELETE FROM plan_entrenamiento WHERE id_plan = ?", (self._id_plan,)
            )
        self._id_plan = None

    # --- Listados ---

    @classmethod
    def _desde_fila(cls, fila):
        return cls(
            id_plan=fila["id_plan"],
            nombre=fila["nombre"],
            descripcion=fila["descripcion"],
            nivel=fila["nivel"],
            duracion_semanas=fila["duracion_semanas"],
            id_entrenador=fila["id_entrenador"],
            id_cliente=fila["id_cliente"],
            nombre_entrenador=fila["entrenador_nombre"],
            apellido_entrenador=fila["entrenador_apellido"],
            nombre_cliente=fila["cliente_nombre"],
            apellido_cliente=fila["cliente_apellido"],
        )

    @staticmethod
    def _consulta_base():
        return (
            "SELECT p.*, e.nombre AS entrenador_nombre, e.apellido AS entrenador_apellido, "
            "c.nombre AS cliente_nombre, c.apellido AS cliente_apellido "
            "FROM plan_entrenamiento p "
            "JOIN entrenador e ON e.id_entrenador = p.id_entrenador "
            "JOIN cliente c ON c.id_cliente = p.id_cliente"
        )

    @classmethod
    def listar_todos(cls):
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " ORDER BY c.apellido, p.nombre"
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        """Planes asignados a un cliente."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " WHERE p.id_cliente = ? ORDER BY p.nombre",
                (id_cliente,),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]

    @classmethod
    def listar_por_entrenador(cls, id_entrenador):
        """Planes elaborados por un entrenador (consulta desde el entrenador)."""
        with conexion() as conn:
            filas = conn.execute(
                cls._consulta_base() + " WHERE p.id_entrenador = ? ORDER BY c.apellido, p.nombre",
                (id_entrenador,),
            ).fetchall()
        return [cls._desde_fila(f) for f in filas]