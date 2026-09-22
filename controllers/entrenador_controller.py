"""Casos de uso de entrenadores."""
from models.entrenador import Entrenador


class EntrenadorController:
    """Coordina las operaciones de entrenadores para la interfaz gráfica."""

    def listar(self):
        """Devuelve todos los entrenadores ordenados por apellido y nombre."""
        return Entrenador.listar_todos()

    def buscar(self, texto):
        """Busca entrenadores por nombre, apellido o especialidad."""
        return Entrenador.buscar_por_texto(texto) if texto.strip() else self.listar()

    def guardar(self, id_entrenador, nombre, apellido, especialidad, telefono, email):
        """Crea o actualiza un entrenador y devuelve su identificador."""
        return Entrenador(id_entrenador=id_entrenador, nombre=nombre, apellido=apellido,
                          especialidad=especialidad, telefono=telefono, email=email).guardar()

    def eliminar(self, id_entrenador):
        """Elimina el entrenador indicado por su identificador."""
        Entrenador(id_entrenador=id_entrenador).eliminar()
