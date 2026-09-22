"""Casos de uso de pagos."""
from models.membresia import Membresia
from models.pago import Pago


class PagoController:
    """Coordina el registro y mantenimiento de pagos."""

    ESTADOS = Pago.ESTADOS

    def listar_membresias(self):
        """Devuelve las membresías disponibles para asociar pagos."""
        return Membresia.listar_todas()

    def listar(self):
        """Devuelve todos los pagos con sus datos de membresía y cliente."""
        return Pago.listar_todas()

    def guardar(self, id_pago, id_membresia, monto, fecha_pago, estado):
        """Crea o actualiza un pago y devuelve su identificador."""
        return Pago(id_pago=id_pago, id_membresia=id_membresia, monto=monto,
                    fecha_pago=fecha_pago, estado=estado).guardar()

    def eliminar(self, id_pago):
        """Elimina el pago indicado por su identificador."""
        Pago(id_pago=id_pago).eliminar()
