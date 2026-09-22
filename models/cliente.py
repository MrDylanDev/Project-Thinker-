"""Modelo Cliente: persona que compra membresías y recibe planes."""
from datetime import date

from data.database import conexion
from .persona import Persona


class Cliente(Persona):
    """Representa un cliente y encapsula su persistencia en SQLite."""

    def __init__(self, id_cliente=None, nombre="", apellido="", telefono="",
                 email="", documento="", fecha_registro=None):
        """Crea un cliente; la fecha por defecto es la fecha actual."""
        super().__init__(nombre, apellido, telefono, email)
        self._id_cliente = id_cliente
        self.documento = documento
        self.fecha_registro = fecha_registro or date.today().isoformat()

    @property
    def id_cliente(self):
        return self._id_cliente

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        self._documento = str(valor or "").strip()

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @fecha_registro.setter
    def fecha_registro(self, valor):
        try:
            date.fromisoformat(str(valor or "").strip())
        except ValueError:
            raise ValueError("La fecha de registro debe tener formato YYYY-MM-DD.")
        self._fecha_registro = str(valor).strip()

    def guardar(self):
        """Inserta o actualiza el cliente según tenga id_cliente asignado."""
        with conexion() as conn:
            if self._id_cliente is None:
                cursor = conn.execute(
                    """INSERT INTO cliente (nombre, apellido, telefono, email,
                                            documento, fecha_registro)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (self._nombre, self._apellido, self._telefono, self._email,
                     self._documento, self._fecha_registro),
                )
                self._id_cliente = cursor.lastrowid
            else:
                conn.execute(
                    """UPDATE cliente
                       SET nombre = ?, apellido = ?, telefono = ?, email = ?,
                           documento = ?, fecha_registro = ?
                       WHERE id_cliente = ?""",
                    (self._nombre, self._apellido, self._telefono, self._email,
                     self._documento, self._fecha_registro, self._id_cliente),
                )
        return self._id_cliente

    def eliminar(self):
        """Elimina el cliente y sus relaciones dependientes mediante FK."""
        if self._id_cliente is None:
            return
        with conexion() as conn:
            conn.execute("DELETE FROM cliente WHERE id_cliente = ?", (self._id_cliente,))
        self._id_cliente = None

    @staticmethod
    def _desde_fila(fila):
        """Convierte una fila SQLite en una instancia de Cliente."""
        return Cliente(
            id_cliente=fila["id_cliente"],
            nombre=fila["nombre"],
            apellido=fila["apellido"],
            telefono=fila["telefono"],
            email=fila["email"],
            documento=fila["documento"],
            fecha_registro=fila["fecha_registro"],
        )

    @staticmethod
    def listar_todos():
        """Obtiene todos los clientes ordenados por apellido y nombre."""
        with conexion() as conn:
            filas = conn.execute(
                "SELECT * FROM cliente ORDER BY apellido, nombre"
            ).fetchall()
        return [Cliente._desde_fila(f) for f in filas]

    @staticmethod
    def buscar_por_id(id_cliente):
        """Obtiene un cliente por ID o devuelve ``None`` si no existe."""
        with conexion() as conn:
            fila = conn.execute(
                "SELECT * FROM cliente WHERE id_cliente = ?", (id_cliente,)
            ).fetchone()
        return Cliente._desde_fila(fila) if fila else None

    @staticmethod
    def buscar_por_texto(texto):
        """Busca coincidencias parciales en nombre, apellido o documento."""
        texto = f"%{texto.strip()}%"
        with conexion() as conn:
            filas = conn.execute(
                """SELECT * FROM cliente
                   WHERE nombre LIKE ? OR apellido LIKE ? OR documento LIKE ?
                   ORDER BY apellido, nombre""",
                (texto, texto, texto),
            ).fetchall()
        return [Cliente._desde_fila(f) for f in filas]

    def __str__(self):
        return f"{self.nombre_completo()} (Doc: {self._documento or 's/n'})"