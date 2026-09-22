"""Casos de uso de reportes."""
from models.cliente import Cliente
from models.membresia import Membresia
from models.pago import Pago
from models.plan_entrenamiento import PlanEntrenamiento


class ReporteController:
    """Prepara consultas agregadas para la pantalla de reportes."""

    def listar_clientes(self):
        """Devuelve los clientes disponibles para consultar su historial."""
        return Cliente.listar_todos()

    def membresias_por_vencer(self, dias):
        """Combina membresías próximas a vencer y membresías vencidas."""
        return Membresia.listar_proximas_a_vencer(dias) + Membresia.listar_vencidas()

    def pagos_pendientes(self):
        """Devuelve la cartera de pagos que siguen pendientes."""
        return Pago.clientes_con_pagos_pendientes()

    def historial_cliente(self, id_cliente):
        """Agrupa membresías, pagos y planes pertenecientes a un cliente."""
        return {
            "membresias": Membresia.listar_por_cliente(id_cliente),
            "pagos": Pago.listar_por_cliente(id_cliente),
            "planes": PlanEntrenamiento.listar_por_cliente(id_cliente),
        }
