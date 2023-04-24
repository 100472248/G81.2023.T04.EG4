from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
import json
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_shipping import OrderShipping
from datetime import datetime
from .order_delivered import OrderDelivered


class JsonStore:
    def __init__(self):
        pass

    @staticmethod
    def save_data(data_list, file_store):
        try:
            with open(file_store, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex

    @staticmethod
    def find_data(data_find, data_list, data):
        for item in data_list:
            if item[data] == data_find:
                return item
        return None

    @staticmethod
    def load_store(file_store):
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so init my data_list
            data_list = None
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data_list

    def save_store(self, data: OrderRequest):
        """Method for saving the orders store"""
        file_store = JSON_FILES_PATH + "orders_store.json"
        data_list = self.load_store(file_store)
        if data_list is None:
            data_list = []
        item = self.find_data(data.order_id, data_list, "_OrderRequest__order_id")
        if item is None:
            data_list.append(data.__dict__)
        else:
            raise OrderManagementException("order_id is already registered in orders_store")
        self.save_data(data_list, file_store)
        return True

    def save_orders_shipped(self, shipment: OrderShipping):
        """Saves the shipping object into a file"""
        shipments_store_file = JSON_FILES_PATH + "shipments_store.json"
        data_list = self.load_store(shipments_store_file)
        if data_list is None:
            data_list = []
        # append the shipments list
        data_list.append(shipment.__dict__)
        self.save_data(data_list, shipments_store_file)

    def save_delivery_store(self, tracking_code: OrderDelivered):
        shipments_file = JSON_FILES_PATH + "shipments_delivered.json"
        data_list = self.load_store(shipments_file)
        # append the delivery info
        data_list.append(tracking_code.__dict__)
        self.save_data(data_list, shipments_file)

    def find_tracking_code(self, data_list, tracking_code):
        item = self.find_data(tracking_code, data_list, "_OrderShipping__tracking_code")
        if item is None:
            raise OrderManagementException("tracking_code is not found")
        else:
            delivery_day_timestamp = item["_OrderShipping__delivery_day"]
        return delivery_day_timestamp

    def read_shipping_store(self):
        shipments_store_file = JSON_FILES_PATH + "shipments_store.json"
        # ¿Como se simplificaria con load_store?
        data_list = self.load_store(shipments_store_file)
        if data_list is None:
            raise OrderManagementException("shipments_store not found")
        return data_list