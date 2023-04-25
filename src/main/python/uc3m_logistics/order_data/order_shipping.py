"""Contains the class OrderShipping"""
from datetime import datetime
import hashlib
import re
import json
from freezegun import freeze_time
from uc3m_logistics.order_data.order_request import OrderRequest
from uc3m_logistics.config.order_management_exception import OrderManagementException
from uc3m_logistics.exception.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.data.attribute_tracking_code import TrackingCode


# pylint: disable=too-many-instance-attributes
class OrderShipping:
    """Class representing the shipping of an order"""

    def __init__(self, input_file):
        self.__json_content = self.validate_product(input_file)
        self.__delivery_email, self.__order_id = self.check_product(self.__json_content)
        self.__product_id, self.__order_type = self.check_order_id(self.__json_content)
        self.__alg = "SHA-256"
        self.__type = "DS"
        justnow = datetime.utcnow()
        self.__issued_at = datetime.timestamp(justnow)
        if self.__order_type == "Regular":
            delivery_days = 7
        else:
            delivery_days = 1
        # timestamp is represneted in seconds.microseconds
        # __delivery_day must be expressed in senconds to be added to the timestap
        self.__delivery_day = self.__issued_at + (delivery_days * 24 * 60 * 60)
        self.__tracking_code = TrackingCode(hashlib.sha256(self.__signature_string().encode()).hexdigest()).value

    def __signature_string(self):
        """Composes the string to be used for generating the tracking_code"""
        return "{alg:" + self.__alg + ",typ:" + self.__type + ",order_id:" + \
            self.__order_id + ",issuedate:" + str(self.__issued_at) + \
            ",deliveryday:" + str(self.__delivery_day) + "}"

    @property
    def product_id(self):
        """Property that represents the product_id of the order"""
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        self.__product_id = value

    @property
    def order_id(self):
        """Property that represents the order_id"""
        return self.__order_id

    @order_id.setter
    def order_id(self, value):
        self.__order_id = value

    @property
    def email(self):
        """Property that represents the email of the client"""
        return self.__delivery_email

    @email.setter
    def email(self, value):
        self.__delivery_email = value

    @property
    def tracking_code(self):
        """returns the tracking code"""
        return self.__tracking_code

    @property
    def issued_at(self):
        """Returns the issued at value"""
        return self.__issued_at

    @issued_at.setter
    def issued_at(self, value):
        self.__issued_at = value

    @property
    def delivery_day(self):
        """Returns the delivery day for the order"""
        return self.__delivery_day

    @staticmethod
    def check_product(data):
        """Analiza todos los campos del producto a enviar"""
        regex_id = re.compile(r"[0-9a-fA-F]{32}$")
        if not regex_id.fullmatch(data["OrderID"]):
            raise OrderManagementException("order id is not valid")
        regex_email = re.compile(r"^[a-z0-9]+([._]?[a-z0-9]+)+@(\w+[.])+\w{2,3}$")
        if not regex_email.fullmatch(data["ContactEmail"]):
            raise OrderManagementException("contact email is not valid")
        return data["ContactEmail"], data["OrderID"]

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
        return order.product_id, order.order_type


