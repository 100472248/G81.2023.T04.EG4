from .attribute import Attribute
from uc3m_logistics.order_management_exception import OrderManagementException


class ProductId(Attribute):
    def __init__(self, attr_value):
        self._error_message = "Invalid EAN13 code string"
        self._validation_pattern = r"^[0-9]{13}$"
        self._attr_value = self._validate(attr_value)

    def _validate(self, attr_value):
        """Method for validating an ean13 code"""
        checksum = 0
        code_read = -1
        super()._validate(attr_value)

        for cifra, digit in enumerate(attr_value):
            if cifra == 12:
                code_read = int(digit)
            elif cifra % 2 != 0:
                checksum += int(digit) * 3
            else:
                checksum += int(digit)
        control_digit = (10 - (checksum % 10)) % 10
        if code_read != control_digit:
            raise OrderManagementException("Invalid EAN13 control digit")
        return attr_value
