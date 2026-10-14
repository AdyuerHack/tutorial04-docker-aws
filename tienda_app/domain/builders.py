from decimal import Decimal

from .logic import CalculadorImpuestos
from ..models import Orden


class OrdenBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._libro = None
        self._items = []
        self._cantidad = 1
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self  # Permite Fluent Interface

    def con_productos(self, productos):
        self._items = productos
        if productos:
            self._libro = productos[0]
        return self

    def con_libro(self, libro):
        self._libro = libro
        return self

    def con_cantidad(self, cantidad):
        self._cantidad = cantidad
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._libro and not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        if self._items:
            subtotal = sum(p.precio for p in self._items)
            total = round(Decimal(str(subtotal)) * Decimal('1.19'), 2)
            libro_obj = self._libro or self._items[0]
        else:
            total_unitario = CalculadorImpuestos.obtener_total_con_iva(self._libro.precio)
            total = round(Decimal(str(total_unitario)) * self._cantidad, 2)
            libro_obj = self._libro

        orden = Orden.objects.create(
            usuario=self._usuario,
            libro=libro_obj,
            total=total,
            direccion_envio=self._direccion,
        )
        self.reset()
        return orden
