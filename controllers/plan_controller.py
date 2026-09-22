"""Casos de uso de planes de entrenamiento."""
from models.cliente import Cliente
from models.entrenador import Entrenador
from models.plan_entrenamiento import NIVELES, PlanEntrenamiento


class PlanController:
    """Coordina los casos de uso de planes de entrenamiento."""

    def listar_clientes(self):
        """Devuelve los clientes que pueden recibir un plan."""
        return Cliente.listar_todos()

    def listar_entrenadores(self):
        """Devuelve los entrenadores que pueden elaborar un plan."""
        return Entrenador.listar_todos()

    def listar(self):
        """Devuelve todos los planes con cliente y entrenador asociados."""
        return PlanEntrenamiento.listar_todos()

    def guardar(self, id_plan, nombre, descripcion, nivel, duracion_semanas,
                id_entrenador, id_cliente):
        """Crea o actualiza un plan y devuelve su identificador."""
        return PlanEntrenamiento(
            id_plan=id_plan, nombre=nombre, descripcion=descripcion, nivel=nivel,
            duracion_semanas=duracion_semanas, id_entrenador=id_entrenador,
            id_cliente=id_cliente,
        ).guardar()

    def eliminar(self, id_plan):
        """Elimina el plan indicado por su identificador."""
        PlanEntrenamiento(id_plan=id_plan).eliminar()
