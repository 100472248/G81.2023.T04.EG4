"""Module"""
from datetime import datetime
from uc3m_logistics.attribute_tracking_code import TrackingCode
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.json_deliver_store import JsonDeliverStore


class OrderDelivered:
    """To check data from the delivered orders"""

    def __init__(self, tracking_code):
        self.__tracking_code = TrackingCode(tracking_code).value
        self.__date_delivered = datetime.utcnow().__str__()

    @staticmethod
    def check_date(del_timestamp):
        """checks if the given date == today's date"""
        today = datetime.today().date()
        delivery_date = datetime.fromtimestamp(del_timestamp).date()
        if delivery_date != today:
            raise OrderManagementException("Today is not the delivery date")

    def check_tracking_code(self):
        """Checks if the tracking_code of the delivery is correct."""
        my_store = JsonDeliverStore()
        my_store.read_shipping_store()
        del_timestamp = my_store.find_tracking_code(self.__tracking_code)
        my_store.save_delivery_store(self.__tracking_code)
        return del_timestamp
