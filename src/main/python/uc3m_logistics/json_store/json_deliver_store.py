"""Module"""
import json
from uc3m_logistics.exception.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.config.order_management_exception import OrderManagementException
from uc3m_logistics.json_store.json_store_master import JsonStoreMaster


class JsonDeliverStore(JsonStoreMaster):
    """Subclass for delivered packages"""

    def __init__(self):
        self._file_path = JSON_FILES_PATH + "shipments_store.json"
        self._data_list = []
        self._tracking_code = "_OrderShipping__tracking_code"
        self._delivery_day = "_OrderShipping__delivery_day"

    def save_orders_shipped(self, shipment):
        """Saves the shipping object into a file"""
        self.load_store()
        # append the shipments list
        self._data_list.append(shipment.__dict__)
        self.save_store()

    def save_delivery_store(self, tracking_code):
        """Save the delivery with its tracking code"""
        self.load_store()
        # append the delivery info
        self._data_list.append(tracking_code)
        self.save_store()

    def find_tracking_code(self, tracking_code):
        """To locate an item with its tracking code"""
        self.load_store()
        self.read_shipping_store()
        item = self.find_by_track(tracking_code)
        if item is None:
            raise OrderManagementException("tracking_code is not found")
        delivery_day_timestamp = item[self._delivery_day]
        return delivery_day_timestamp

    def read_shipping_store(self):
        """It reads the shipping store file"""
        try:
            with open(self._file_path, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        except FileNotFoundError as ex:
            raise OrderManagementException("shipments_store not found") from ex
