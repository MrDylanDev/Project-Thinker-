"""Clase base abstracta para las personas del gimnasio."""
from abc import ABC, abstractmethod


class Persona(ABC):
    """Representa una persona genérica del gimnasio (cliente o entrenador)."""

    def __init__(self, nombre="", apellido="", telefono="", email=""):
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor or "").strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor

    @property
    def apellido(self):
        return self._apellido

    @apellido.setter
    def apellido(self, valor):
        valor = str(valor or "").strip()
        if not valor:
            raise ValueError("El apellido no puede estar vacío.")
        self._apellido = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = str(valor or "").strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        valor = str(valor or "").strip()
        if valor and "@" not in valor:
            raise ValueError("El email no tiene un formato válido.")
        self._email = valor

    def nombre_completo(self):
        """Devuelve 'nombre apellido'."""
        return f"{self._nombre} {self._apellido}".strip()

    def __str__(self):
        return self.nombre_completo()

    @abstractmethod
    def guardar(self):
        """Persiste la persona en la base de datos."""
        raise NotImplementedError