"""..."""
import re
from uc3m_logistics.order_management_exception import OrderManagementException


class Attribute:
    """Masterclass of the attributes"""
    def __init__(self):
        self._attr_value = ""
        self._error_message = ""
        self._validation_pattern = r""

    def _validate(self, value):
        myregex = re.compile(self._validation_pattern)
        if not myregex.fullmatch(value):
            raise OrderManagementException(self._error_message)
        return value

    @property
    def value(self):
        """Para crear la property de attr_value"""
        return self._attr_value

    @value.setter
    def value(self, attr_value):
        self._attr_value = attr_value
