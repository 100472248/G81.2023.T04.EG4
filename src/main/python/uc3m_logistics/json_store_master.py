"""Module"""
import json
from uc3m_logistics.order_management_exception import OrderManagementException


class JsonStoreMaster:
    """Clase master de los almacenes"""
    def __init__(self):
        self._file_path = ""
        self._data_list = []
        self._id_field = ""
        self._tracking_code = ""

    def load_store(self):
        """Inicializa el almacén."""
        try:
            with open(self._file_path, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so init my data_list
            self._data_list = []
        except json.JSONDecodeError as ex:
            raise OrderManagementException("JSON Decode Error - Wrong JSON Format") from ex

    def save_store(self):
        """Guarda el almacén"""
        try:
            with open(self._file_path, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise OrderManagementException("Wrong file or file path") from ex

    def find_data(self, data_find):
        """Para encontrar el dato."""
        for item in self._data_list:
            if item[self._id_field] == data_find:
                return item
        return None

    def find_by_track(self, track_code):
        """For finding the item with this tracking code"""
        for item in self._data_list:
            if item[self._tracking_code] == track_code:
                return item
        return None

    def add_item(self, item):
        """Añadir un nuevo item de forma general"""
        self.load_store()
        self._data_list.append(item)
        self.save_store()
