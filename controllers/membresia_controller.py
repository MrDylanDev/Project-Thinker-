"""Casos de uso de membresías."""
from models.cliente import Cliente
from models.membresia import Membresia, PLANES_DURACION, PLANES_VALOR


class MembresiaController:
    """Expone los casos de uso de membresías a la vista."""

    def listar_clientes(self):
        """Devuelve los clientes disponibles para una membresía."""
        return Cliente.listar_todos()

    def listar(self):
        """Devuelve todas las membresías con la información del cliente."""
        return Membresia.listar_todas()

    def guardar(self, id_membresia, id_cliente, tipo, fecha_inicio, estado):
        """Crea o actualiza una membresía y devuelve su identificador."""
        return Membresia(id_membresia=id_membresia, id_cliente=id_cliente, tipo=tipo,
                         fecha_inicio=fecha_inicio, estado=estado or "Activa").guardar()

    def renovar(self, id_membresia):
        """Extiende la membresía y la devuelve al estado activo."""
        membresia = Membresia(id_membresia=id_membresia)
        membresia.renovar()

    def cancelar(self, id_membresia):
        """Marca una membresía como cancelada."""
        membresia = Membresia(id_membresia=id_membresia)
        membresia.cancelar()

    def eliminar(self, id_membresia):
        """Elimina una membresía de la base de datos."""
        Membresia(id_membresia=id_membresia).eliminar()
