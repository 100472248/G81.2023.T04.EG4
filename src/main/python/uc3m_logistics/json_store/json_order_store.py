"""Module"""
from uc3m_logistics.exception.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.config.order_management_exception import OrderManagementException
from uc3m_logistics.json_store.json_store_master import JsonStoreMaster


class JsonOrderStore:
    """Main subclass used for the orders"""
    class __JsonOrderStore(JsonStoreMaster):
        """Private JsonOrderStore"""

        def __init__(self):
            self._file_path = JSON_FILES_PATH + "orders_store.json"
            self._data_list = []
            self._id_field = "_OrderRequest__order_id"

        def add_item(self, item):
            """Only if it isn´t exist in the file"""
            self.load_store()
            found = self.find_data(item.order_id)
            if found is None:
                self._data_list.append(item.__dict__)
            else:
                raise OrderManagementException("order_id is already registered in orders_store")
            self.save_store()

    instance = None

    def __new__(cls):
        if not JsonOrderStore.instance:
            JsonOrderStore.instance = JsonOrderStore.__JsonOrderStore()
        return JsonOrderStore.instance

    def __getattr__(self, nombre):
        return getattr(self.instance, nombre)

    def __setattr__(self, nombre, valor):
        return setattr(self.instance, nombre, valor)
