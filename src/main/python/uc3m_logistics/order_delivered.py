"""Module"""
from datetime import datetime
from uc3m_logistics.attribute_tracking_code import TrackingCode
from uc3m_logistics.order_management_exception import OrderManagementException


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
