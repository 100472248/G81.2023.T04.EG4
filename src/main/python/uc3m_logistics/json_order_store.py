"""Module"""
from uc3m_logistics.order_manager_config import JSON_FILES_PATH
from uc3m_logistics.order_management_exception import OrderManagementException
from uc3m_logistics.json_store_master import JsonStoreMaster


class JsonOrderStore(JsonStoreMaster):
    """Clase master de los almacenes"""

    def __init__(self):
        self._file_path = JSON_FILES_PATH + "orders_store.json"
        self._data_list = []
        self._id_field = "_OrderRequest__order_id"

    def sub_add_item(self, item):
        """Añade el item al almacén si no está."""
        self.load_store()
        found = self.find_data(item.order_id)
        if found is None:
            self._data_list.append(item.__dict__)
        else:
            raise OrderManagementException("order_id is already registered in orders_store")
        self.save_store()
