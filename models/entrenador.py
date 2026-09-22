"""Modelo Entrenador: persona que elabora planes de entrenamiento."""
from data.database import conexion
from .persona import Persona


class Entrenador(Persona):
    def __init__(self, id_entrenador=None, nombre="", apellido="", telefono="",
                 email="", especialidad=""):
        super().__init__(nombre, apellido, telefono, email)
        self._id_entrenador = id_entrenador
        self.especialidad = especialidad

    @property
    def id_entrenador(self):
        return self._id_entrenador

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        self._especialidad = str(valor or "").strip()

    def guardar(self):
        """Inserta o actualiza el entrenador según tenga id_entrenador asignado."""
        with conexion() as conn:
            if self._id_entrenador is None:
                cursor = conn.execute(
                    """INSERT INTO entrenador (nombre, apellido, telefono, email,
                                               especialidad)
                       VALUES (?, ?, ?, ?, ?)""",
                    (self._nombre, self._apellido, self._telefono, self._email,
                     self._especialidad),
                )
                self._id_entrenador = cursor.lastrowid
            else:
                conn.execute(
                    """UPDATE entrenador
                       SET nombre = ?, apellido = ?, telefono = ?, email = ?,
                           especialidad = ?
                       WHERE id_entrenador = ?""",
                    (self._nombre, self._apellido, self._telefono, self._email,
                     self._especialidad, self._id_entrenador),
                )
        return self._id_entrenador

    def eliminar(self):
        if self._id_entrenador is None:
            return
        with conexion() as conn:
            conn.execute(
                "DELETE FROM entrenador WHERE id_entrenador = ?", (self._id_entrenador,)
            )
        self._id_entrenador = None

    @staticmethod
    def _desde_fila(fila):
        return Entrenador(
            id_entrenador=fila["id_entrenador"],
            nombre=fila["nombre"],
            apellido=fila["apellido"],
            telefono=fila["telefono"],
            email=fila["email"],
            especialidad=fila["especialidad"],
        )

    @staticmethod
    def listar_todos():
        with conexion() as conn:
            filas = conn.execute(
                "SELECT * FROM entrenador ORDER BY apellido, nombre"
            ).fetchall()
        return [Entrenador._desde_fila(f) for f in filas]

    @staticmethod
    def buscar_por_id(id_entrenador):
        with conexion() as conn:
            fila = conn.execute(
                "SELECT * FROM entrenador WHERE id_entrenador = ?", (id_entrenador,)
            ).fetchone()
        return Entrenador._desde_fila(fila) if fila else None

    @staticmethod
    def buscar_por_texto(texto):
        texto = f"%{texto.strip()}%"
        with conexion() as conn:
            filas = conn.execute(
                """SELECT * FROM entrenador
                   WHERE nombre LIKE ? OR apellido LIKE ? OR especialidad LIKE ?
                   ORDER BY apellido, nombre""",
                (texto, texto, texto),
            ).fetchall()
        return [Entrenador._desde_fila(f) for f in filas]

    def __str__(self):
        return f"{self.nombre_completo()} ({self._especialidad or 's/n'})"