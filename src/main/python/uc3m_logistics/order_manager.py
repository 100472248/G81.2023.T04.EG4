"""Module """
import json
from datetime import datetime
from freezegun import freeze_time
from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_shipping import OrderShipping
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.check_methods import CheckMethods


class OrderManager:
    """Class for providing the methods for managing the orders process"""

    def __init__(self):
        pass

    @staticmethod
    def save_store(data: OrderRequest):
        """Method for saving the orders store"""
        file_store = JSON_FILES_PATH + "orders_store.json"
        try:
            with open(file_store, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so init my data_list
            data_list = []
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        found = False
        for item in data_list:
            if item["_OrderRequest__order_id"] == data.order_id:
                found = True
        if found is False:
            data_list.append(data.__dict__)
        else:
            raise OrderManagementException("order_id is already registered in orders_store")
        try:
            with open(file_store, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex
        return True

    @staticmethod
    def save_fast(data: OrderRequest):
        """Method for saving the orders store"""
        orders_store = JSON_FILES_PATH + "orders_store.json"
        with open(orders_store, "r+", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
            data_list.append(data.__dict__)
            file.seek(0)
            json.dump(data_list, file, indent=2)

    @staticmethod
    def save_orders_shipped(shipment: OrderShipping):
        """Saves the shipping object into a file"""
        shipments_store_file = JSON_FILES_PATH + "shipments_store.json"
        try:
            with open(shipments_store_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so init my data_list
            data_list = []
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # append the shipments list
        data_list.append(shipment.__dict__)

        try:
            with open(shipments_store_file, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex

    # pylint: disable=too-many-arguments
    def register_order(self, product_id, order_type,
                       address, phone_number, zip_code):
        """Register the orders into the order's file"""
        my_order = OrderRequest(product_id, order_type, address,
                                phone_number, zip_code)
        self.save_store(my_order)
        return my_order.order_id

    # pylint: disable=too-many-locals

    def send_product(self, input_file):
        """Sends the order included in the input_file"""
        try:
            # check all the information
            my_sign = OrderShipping(input_file)
        except KeyError as ex:
            raise OrderManagementException("Bad label") from ex
        # save the OrderShipping in shipments_store.json
        self.save_orders_shipped(my_sign)
        return my_sign.tracking_code

    @staticmethod
    def check_order_id(data):
        """Para estudiar si el ID es correcto."""
        file_store = JSON_FILES_PATH + "orders_store.json"
        with open(file_store, "r", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
        found = False
        order = None
        for item in data_list:
            # set the time when the order was registered for checking the md5
            with freeze_time(datetime.fromtimestamp(item["_OrderRequest__time_stamp"]).date()):
                order = OrderRequest(product_id=item["_OrderRequest__product_id"],
                                     delivery_address=item["_OrderRequest__delivery_address"],
                                     order_type=item["_OrderRequest__order_type"],
                                     phone_number=item["_OrderRequest__phone_number"],
                                     zip_code=item["_OrderRequest__zip_code"])
            if order.order_id != data["OrderID"]:
                raise OrderManagementException("Orders' data have been manipulated")
            found = True
        if not found:
            raise OrderManagementException("order_id not found")
        return order

    @staticmethod
    def deliver_product(tracking_code):
        """Register the delivery of the product"""
        CheckMethods().check_delivery(tracking_code)
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
        return True
