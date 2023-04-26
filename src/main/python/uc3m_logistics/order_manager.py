"""Module """
from uc3m_logistics.order_data.order_request import OrderRequest
from uc3m_logistics.config.order_management_exception import OrderManagementException
from uc3m_logistics.order_data.order_shipping import OrderShipping
from uc3m_logistics.json_store.json_deliver_store import JsonDeliverStore
from uc3m_logistics.json_store.json_order_store import JsonOrderStore
from uc3m_logistics.order_data.order_delivered import OrderDelivered


class OrderManager:
    """Main class for providing the methods for managing the orders process"""
    class __OrderManager:
        """Private OrderManager"""

        def __init__(self):
            pass

        # pylint: disable=too-many-arguments
        @staticmethod
        def register_order(product_id, order_type,
                           address, phone_number, zip_code):
            """Register the orders into the order's file"""
            my_order = OrderRequest(product_id, order_type, address,
                                    phone_number, zip_code)
            my_store = JsonOrderStore()
            my_store.add_item(my_order)
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
            my_store = JsonDeliverStore()
            my_store.save_orders_shipped(my_sign)
            return my_sign.tracking_code

        @staticmethod
        def deliver_product(tracking_code):
            """Register the delivery of the product"""
            my_deliver = OrderDelivered(tracking_code)
            del_timestamp = my_deliver.check_tracking_code()
            my_deliver.check_date(del_timestamp)
            return True

    instance = None

    def __new__(cls):
        if not OrderManager.instance:
            OrderManager.instance = OrderManager.__OrderManager()
        return OrderManager.instance

    def __getattr__(self, nombre):
        return getattr(self.instance, nombre)

    def __setattr__(self, nombre, valor):
        return setattr(self.instance, nombre, valor)
