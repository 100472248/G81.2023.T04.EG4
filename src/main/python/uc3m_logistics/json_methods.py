"""..."""
import json
import re
from datetime import datetime
from freezegun import freeze_time
from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_shipping import OrderShipping
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_manager_config import JSON_FILES_PATH


class Jsonmethods:
    """Clase con las funciones de los json."""
    @staticmethod
    def validate_send_product(order_id, email):
        """Analiza todos los campos del producto a enviar"""
        regex_id = re.compile(r"[0-9a-fA-F]{32}$")
        if not regex_id.fullmatch(order_id):
            raise OrderManagementException("order id is not valid")
        regex_email = re.compile(r"^[a-z0-9]+([\._]?[a-z0-9]+)+[@](\w+[.])+\w{2,3}$")
        if not regex_email.fullmatch(email):
            raise OrderManagementException("contact email is not valid")
        return True
