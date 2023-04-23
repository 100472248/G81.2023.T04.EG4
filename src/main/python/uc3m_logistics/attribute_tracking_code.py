from .attribute import Attribute


class TrackingCode(Attribute):
    def __init__(self, attr_value):
        self._error_message = "tracking_code format is not valid"
        self._validation_pattern = r"[0-9a-fA-F]{64}$"
        self._attr_value = self._validate(attr_value)