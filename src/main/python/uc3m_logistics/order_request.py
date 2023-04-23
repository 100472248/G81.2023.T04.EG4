"""MODULE: order_request. Contains the order request class"""
import hashlib
import json
import re
from datetime import datetime
from uc3m_logistics.order_management_exception import OrderManagementException


class OrderRequest:
    """Class representing the register of the order in the system"""

    # pylint: disable=too-many-arguments
    def __init__(self, product_id, order_type,
                 delivery_address, phone_number, zip_code):
        self.__product_id = self.validate_ean13(product_id)
        self.__delivery_address = self.validate_attr(delivery_address,
                                                     r"^(?=^.{20,100}$)(([a-zA-Z0-9]+\s)+[a-zA-Z0-9]+)$",
                                                     "address is not valid")
        self.__order_type = self.validate_attr(order_type, r"(Regular|Premium)", "order_type is not valid")
        self.__phone_number = self.validate_attr(phone_number, r"^(\+)[0-9]{11}", "phone number is not valid")
        self.__zip_code = self.validate_zip_code(zip_code)
        justnow = datetime.utcnow()
        self.__time_stamp = datetime.timestamp(justnow)
        self.__order_id = hashlib.md5(self.__str__().encode()).hexdigest()

    def __str__(self):
        return "OrderRequest:" + json.dumps(self.__dict__)

    @property
    def delivery_address(self):
        """Property representing the address where the product
        must be delivered"""
        return self.__delivery_address

    @delivery_address.setter
    def delivery_address(self, value):
        self.__delivery_address = value

    @property
    def order_type(self):
        """Property representing the type of order: REGULAR or PREMIUM"""
        return self.__order_type

    @order_type.setter
    def order_type(self, value):
        self.__order_type = value

    @property
    def phone_number(self):
        """Property representing the client's phone number"""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, value):
        self.__phone_number = value

    @staticmethod
    def validate_attr(atributo, patron, mensaje_error: str):
        """Función para validar los distintos atributos"""
        myregex = re.compile(patron)
        if not myregex.fullmatch(atributo):
            raise OrderManagementException(mensaje_error)
        return atributo

    @property
    def product_id(self):
        """Property representing the products  EAN13 code"""
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        self.__product_id = value

    @staticmethod
    def validate_ean13(ean13):
        """Method for validating an ean13 code"""
        checksum = 0
        ultima_cifra = -1
        regex_ean13 = re.compile("^[0-9]{13}$")
        if regex_ean13.fullmatch(ean13) is None:
            raise OrderManagementException("Invalid EAN13 code string")
        for cifra, digit in enumerate(ean13):
            if cifra == 12:
                ultima_cifra = int(digit)
            elif cifra % 2 != 0:
                checksum += int(digit) * 3
            else:
                checksum += int(digit)
        control_digit = (10 - (checksum % 10)) % 10
        if ultima_cifra != control_digit:
            raise OrderManagementException("Invalid EAN13 control digit")
        return ean13

    @property
    def time_stamp(self):
        """Read-only property that returns the timestamp of the request"""
        return self.__time_stamp

    @property
    def order_id(self):
        """Returns the md5 signature"""
        return self.__order_id

    @property
    def zip_code(self):
        """Returns the order's zip_code"""
        return self.__zip_code

    @staticmethod
    def validate_zip_code(zip_code) -> str:
        """Estudia si el código zip es válido."""
        if zip_code.isnumeric() and len(zip_code) == 5:
            if int(zip_code) > 52999 or int(zip_code) < 1000:
                raise OrderManagementException("zip_code is not valid")
        else:
            raise OrderManagementException("zip_code format is not valid")
        return zip_code
