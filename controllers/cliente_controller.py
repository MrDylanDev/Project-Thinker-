"""Casos de uso de clientes."""
from models.cliente import Cliente


class ClienteController:
    """Coordina las operaciones de clientes entre la vista y el modelo."""

    def listar(self):
        """Devuelve todos los clientes ordenados por apellido y nombre."""
        return Cliente.listar_todos()

    def buscar(self, texto):
        """Busca clientes por nombre, apellido o documento."""
        return Cliente.buscar_por_texto(texto) if texto.strip() else self.listar()

    def guardar(self, id_cliente, nombre, apellido, documento, telefono, email):
        """Crea o actualiza un cliente y devuelve su identificador."""
        return Cliente(id_cliente=id_cliente, nombre=nombre, apellido=apellido,
                       documento=documento, telefono=telefono, email=email).guardar()

    def eliminar(self, id_cliente):
        """Elimina el cliente indicado por su identificador."""
        Cliente(id_cliente=id_cliente).eliminar()
