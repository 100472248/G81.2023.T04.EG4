"""..."""
import json
import re
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from .attribute_tracking_code import TrackingCode
from datetime import datetime


class CheckMethods:
    """Clase con las funciones relacionadas con comprobar la validez de los diversos productos o atributos
    de order_request y order_shipping para usarlos en order_manager"""

    def __init__(self):
        pass

    @staticmethod
    def check_delivery(tracking_code):
        """Checks whether the tracking_code is in shipments_store and delivery_day is
         correct"""
        TrackingCode(tracking_code)
        shipments_store_file = JSON_FILES_PATH + "shipments_store.json"
        try:
            with open(shipments_store_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        except FileNotFoundError as ex:
            raise OrderManagementException("shipments_store not found") from ex

        found = False
        delivery_day_timestamp = None
        for item in data_list:
            if item["_OrderShipping__tracking_code"] == tracking_code:
                found = True
                delivery_day_timestamp = item["_OrderShipping__delivery_day"]
        if not found:
            raise OrderManagementException("tracking_code is not found")

        today = datetime.today().date()
        delivery_date = datetime.fromtimestamp(delivery_day_timestamp).date()
        if delivery_date != today:
            raise OrderManagementException("Today is not the delivery date")

    @staticmethod
    def check_product(order_id, email):
        """Analiza todos los campos del producto a enviar"""
        regex_id = re.compile(r"[0-9a-fA-F]{32}$")
        if not regex_id.fullmatch(order_id):
            raise OrderManagementException("order id is not valid")
        regex_email = re.compile(r"^[a-z0-9]+([._]?[a-z0-9]+)+@(\w+[.])+\w{2,3}$")
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
