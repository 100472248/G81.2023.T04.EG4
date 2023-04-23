"""..."""
import json
from datetime import datetime
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.attribute_tracking_code import TrackingCode


class CheckMethods:
    """Clase que comprueba las funciones del deliver-product."""

    def __init__(self):
        pass

    def check_delivery(self, tracking_code):
        """Checks whether the delivery is correct or not"""
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

        delivery_day = datetime.fromtimestamp(delivery_day_timestamp).date()
        self.check_delivery_date(delivery_day)

    @staticmethod
    def check_delivery_date(delivery_day):
        """checks if the given date == today's date"""
        today = datetime.today().date()
        if delivery_day != today:
            raise OrderManagementException("Today is not the delivery date")
