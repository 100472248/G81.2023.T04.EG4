"""Module """
import re
import json
from datetime import datetime
from freezegun import freeze_time
from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_shipping import OrderShipping
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.send_methods import Sendmethods


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
        shimpents_store_file = JSON_FILES_PATH + "shipments_store.json"
        try:
            with open(shimpents_store_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so init my data_list
            data_list = []
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # append the shipments list
        data_list.append(shipment.__dict__)

        try:
            with open(shimpents_store_file, "w", encoding="utf-8", newline="") as file:
                json.dump(data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex

    # pylint: disable=too-many-arguments
    def register_order(self, product_id, order_type,
                       address, phone_number, zip_code):
        """Register the orders into the order's file"""
        my_order = OrderRequest(product_id, order_type, address,
                                phone_number, zip_code)
        self.validate_ean13(product_id)
        self.validate_attr(order_type, r"(Regular|Premium)", "order_type is not valid")
        self.validate_attr(address, r"^(?=^.{20,100}$)(([a-zA-Z0-9]+\s)+[a-zA-Z0-9]+)$",
                           "address is not valid")
        self.validate_attr(phone_number, r"^(\+)[0-9]{11}", "phone number is not valid")
        self.validate_zip_code(zip_code)
        self.save_store(my_order)
        return my_order.order_id

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
        return True

    @staticmethod
    def validate_attr(atributo, patron, mensaje_error: str):
        """Función para validar los distintos atributos"""
        myregex = re.compile(patron)
        if not myregex.fullmatch(atributo):
            raise OrderManagementException(mensaje_error)
        return True

    @staticmethod
    def validate_zip_code(zip_code):
        """Estudia si el código zip es válido."""
        if zip_code.isnumeric() and len(zip_code) == 5:
            if int(zip_code) > 52999 or int(zip_code) < 1000:
                raise OrderManagementException("zip_code is not valid")
        else:
            raise OrderManagementException("zip_code format is not valid")
        return True

    @staticmethod
    def validate_tracking_code(tracking_code):
        """Method for validating sha256 values"""
        myregex = re.compile(r"[0-9a-fA-F]{64}$")
        if not myregex.fullmatch(tracking_code):
            raise OrderManagementException("tracking_code format is not valid")

    # pylint: disable=too-many-locals

    def send_product(self, input_file):
        """Sends the order included in the input_file"""
        try:
            # check all the information
            check_send = Sendmethods()
            data = check_send.validate_product(input_file)
            check_send.check_product(data["OrderID"], data["ContactEmail"])
        except KeyError as ex:
            raise OrderManagementException("Bad label") from ex
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
        my_sign = OrderShipping(product_id=order.product_id,
                                order_id=data["OrderID"],
                                order_type=order.order_type,
                                delivery_email=data["ContactEmail"])
        # save the OrderShipping in shipments_store.json
        self.save_orders_shipped(my_sign)
        return my_sign.tracking_code

    def check_delivery(self, tracking_code):
        """Checks whether the tracking_code is in shipments_store and delivery_day is
         correct"""
        self.validate_tracking_code(tracking_code)
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

    def deliver_product(self, tracking_code):
        """Register the delivery of the product"""
        self.check_delivery(tracking_code)
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
