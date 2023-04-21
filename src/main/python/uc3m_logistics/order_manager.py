"""Module """
import re
import json
from datetime import datetime
from freezegun import freeze_time
from uc3m_logistics.order_request import OrderRequest
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.order_shipping import OrderShipping
from uc3m_logistics.order_manager_config import JSON_FILES_PATH


class OrderManager:
    """Class for providing the methods for managing the orders process"""

    def __init__(self):
        pass

    @staticmethod
    def validate_ean13(ean13):
        """Method for validating an ean13 code"""
        checksum = 0
        ultima_cifra = -1
        regex_ean13 = re.compile("^[0-9]{13}$")
        valid_ean13_format = regex_ean13.fullmatch(ean13)
        if valid_ean13_format is None:
            raise OrderManagementException("Invalid EAN13 code string")
        for cifra, digit in enumerate(reversed(ean13)):
            try:
                current_digit = int(digit)
            except ValueError as v_e:
                raise OrderManagementException("Invalid EAN13 code string") from v_e
            if cifra == 0:
                ultima_cifra = current_digit
            else:
                checksum += current_digit * 3 if (cifra % 2 != 0) else current_digit
        control_digit = (10 - (checksum % 10)) % 10
        if (ultima_cifra != -1) and (ultima_cifra == control_digit):
            return True
        raise OrderManagementException("Invalid EAN13 control digit")

    @staticmethod
    def validate_tracking_code(t_c):
        """Method for validating sha256 values"""
        myregex = re.compile(r"[0-9a-fA-F]{64}$")
        if not myregex.fullmatch(t_c):
            raise OrderManagementException("tracking_code format is not valid")

    @staticmethod
    def save_store(data):
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
    def save_fast(data):
        """Method for saving the orders store"""
        orders_store = JSON_FILES_PATH + "orders_store.json"
        with open(orders_store, "r+", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
            data_list.append(data.__dict__)
            file.seek(0)
            json.dump(data_list, file, indent=2)

    @staticmethod
    def save_orders_shipped(shipment):
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
        self.validate_ean13(product_id)
        self.validate_order_type(order_type)
        self.validate_address(address)
        self.validate_phone_number(phone_number)
        self.validate_zip_code(zip_code)
        my_order = OrderRequest(product_id, order_type, address,
                                phone_number, zip_code)
        self.save_store(my_order)
        return my_order.order_id

    @staticmethod
    def validate_order_type(order_type):
        """Estudia si la orden es regular o premium."""
        myregex = re.compile(r"(Regular|Premium)")
        validation = myregex.fullmatch(order_type)
        if not validation:
            raise OrderManagementException("order_type is not valid")
        return True

    @staticmethod
    def validate_address(address):
        """Indica si la dirección es indicada."""
        myregex = re.compile(r"^(?=^.{20,100}$)(([a-zA-Z0-9]+\s)+[a-zA-Z0-9]+)$")
        if not myregex.fullmatch(address):
            raise OrderManagementException("address is not valid")
        return True

    @staticmethod
    def validate_phone_number(phone_number):
        """Valida el número de teléfono."""
        myregex = re.compile(r"^(\+)[0-9]{11}")
        if not myregex.fullmatch(phone_number):
            raise OrderManagementException("phone number is not valid")
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

    # pylint: disable=too-many-locals

    def send_product(self, input_file):
        """Sends the order included in the input_file"""
        try:
            with open(input_file, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            # file is not found
            raise OrderManagementException("File is not found") from ex
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # check all the information
        try:
            myregex = re.compile(r"[0-9a-fA-F]{32}$")
            if not myregex.fullmatch(data["OrderID"]):
                raise OrderManagementException("order id is not valid")
        except KeyError as ex:
            raise OrderManagementException("Bad label") from ex

        try:
            regex_email = r'^[a-z0-9]+([\._]?[a-z0-9]+)+[@](\w+[.])+\w{2,3}$'
            myregex = re.compile(regex_email)
            if not myregex.fullmatch(data["ContactEmail"]):
                raise OrderManagementException("contact email is not valid")
        except KeyError as ex:
            raise OrderManagementException("Bad label") from ex
        file_store = JSON_FILES_PATH + "orders_store.json"
        with open(file_store, "r", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
        found = False
        pro_id = None
        reg_type = None
        for item in data_list:
            # retrieve the orders data
            pro_id = item["_OrderRequest__product_id"]
            reg_type = item["_OrderRequest__order_type"]
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
        my_sign = OrderShipping(product_id=pro_id,
                                order_id=data["OrderID"],
                                order_type=reg_type,
                                delivery_email=data["ContactEmail"])
        # save the OrderShipping in shipments_store.json
        self.save_orders_shipped(my_sign)
        return my_sign.tracking_code

    def deliver_product(self, tracking_code):
        """Register the delivery of the product"""
        self.validate_tracking_code(tracking_code)

        # check if this tracking_code is in shipments_store
        shimpents_store_file = JSON_FILES_PATH + "shipments_store.json"
        try:
            with open(shimpents_store_file, "r", encoding="utf-8", newline="") as file:
                data_list = json.load(file)
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex
        except FileNotFoundError as ex:
            raise OrderManagementException("shipments_store not found") from ex
        # search this tracking_code
        found = False
        del_timestamp = None
        for item in data_list:
            if item["_OrderShipping__tracking_code"] == tracking_code:
                found = True
                del_timestamp = item["_OrderShipping__delivery_day"]
        if not found:
            raise OrderManagementException("tracking_code is not found")

        today = datetime.today().date()
        delivery_date = datetime.fromtimestamp(del_timestamp).date()
        if delivery_date != today:
            raise OrderManagementException("Today is not the delivery date")

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
