"""Modelo Cliente: persona que compra membresías y recibe planes."""
from datetime import date

from data.database import conexion
from .persona import Persona


class Cliente(Persona):
    def __init__(self, id_cliente=None, nombre="", apellido="", telefono="",
                 email="", documento="", fecha_registro=None):
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
        if self._id_cliente is None:
            return
        with conexion() as conn:
            conn.execute("DELETE FROM cliente WHERE id_cliente = ?", (self._id_cliente,))
        self._id_cliente = None

    @staticmethod
    def _desde_fila(fila):
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
        with conexion() as conn:
            filas = conn.execute(
                "SELECT * FROM cliente ORDER BY apellido, nombre"
            ).fetchall()
        return [Cliente._desde_fila(f) for f in filas]

    @staticmethod
    def buscar_por_id(id_cliente):
        with conexion() as conn:
            fila = conn.execute(
                "SELECT * FROM cliente WHERE id_cliente = ?", (id_cliente,)
            ).fetchone()
        return Cliente._desde_fila(fila) if fila else None

    @staticmethod
    def buscar_por_texto(texto):
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