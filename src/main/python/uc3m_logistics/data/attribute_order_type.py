"""Module"""
from uc3m_logistics.data.attribute import Attribute


class OrderType(Attribute):
    """Checks the order type"""
    def __init__(self, attr_value):
        self._error_message = "order_type is not valid"
        self._validation_pattern = r"(Regular|Premium)"
        self._attr_value = self._validate(attr_value)
