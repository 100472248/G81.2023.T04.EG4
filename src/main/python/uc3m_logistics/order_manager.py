"""Module """
import json
from datetime import datetime
from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_shipping import OrderShipping
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.attribute_tracking_code import TrackingCode
from .json_store import JsonStore


class OrderManager:
    """Class for providing the methods for managing the orders process"""

    def __init__(self):
        pass

    # pylint: disable=too-many-arguments
    @staticmethod
    def register_order(product_id, order_type,
                       address, phone_number, zip_code):
        """Register the orders into the order's file"""
        my_order = OrderRequest(product_id, order_type, address,
                                phone_number, zip_code)
        my_store = JsonStore()
        my_store.save_store(my_order)
        return my_order.order_id

    # pylint: disable=too-many-locals
    @staticmethod
    def send_product(input_file):
        """Sends the order included in the input_file"""
        try:
            # check all the information
            my_sign = OrderShipping(input_file)
        except KeyError as ex:
            raise OrderManagementException("Bad label") from ex
        # save the OrderShipping in shipments_store.json
        my_store = JsonStore()
        my_store.save_orders_shipped(my_sign)
        return my_sign.tracking_code

    def deliver_product(self, tracking_code):
        """Register the delivery of the product"""
        TrackingCode(tracking_code)
        data_list = self.read_shipping_store()
        del_timestamp = self.find_tracking_code(data_list, tracking_code)
        self.check_date(del_timestamp)
        self.save_delivery_store(tracking_code)
        return True

    @staticmethod
    def save_delivery_store(tracking_code):
        shipments_file = JSON_FILES_PATH + "shipments_delivered.json"
        try:
            with open(shipments_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so  init my data_list
            data_list = []
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # append the delivery info
        data_list.append(str(tracking_code))
        data_list.append(str(datetime.utcnow()))
        try:
            with open(shipments_file, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex

    @staticmethod
    def check_date(del_timestamp):
        """checks if the given date == today's date"""
        today = datetime.today().date()
        delivery_date = datetime.fromtimestamp(del_timestamp).date()
        if delivery_date != today:
            raise OrderManagementException("Today is not the delivery date")

    @staticmethod
    def find_tracking_code(data_list, tracking_code):
        found = False
        delivery_day_timestamp = None
        for item in data_list:
            if item["_OrderShipping__tracking_code"] == tracking_code:
                found = True
                delivery_day_timestamp = item["_OrderShipping__delivery_day"]
        if not found:
            raise OrderManagementException("tracking_code is not found")
        return delivery_day_timestamp

    @staticmethod
    def read_shipping_store():
        shipments_store_file = JSON_FILES_PATH + "shipments_store.json"
        try:
            with open(shipments_store_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        except FileNotFoundError as ex:
            raise OrderManagementException("shipments_store not found") from ex
        return data_list
