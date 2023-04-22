"""..."""
import json
import re
from uc3m_logistics.order_management_exception import OrderManagementException


class Jsonmethods:
    """Clase con las funciones de los json."""

    @staticmethod
    def check_product(order_id, email):
        """Analiza todos los campos del producto a enviar"""
        regex_id = re.compile(r"[0-9a-fA-F]{32}$")
        if not regex_id.fullmatch(order_id):
            raise OrderManagementException("order id is not valid")
        regex_email = re.compile(r"^[a-z0-9]+([\._]?[a-z0-9]+)+@(\w+[.])+\w{2,3}$")
        if not regex_email.fullmatch(email):
            raise OrderManagementException("contact email is not valid")
        return True

    @staticmethod
    def validate_product(input_file):
        """Checks the order included in the input_file"""
        try:
            with open(input_file, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            # file is not found
            raise OrderManagementException("File is not found") from ex
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data
