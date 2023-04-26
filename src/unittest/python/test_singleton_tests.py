"""Module for testing singleton"""
from unittest import TestCase
from uc3m_logistics import OrderManager
from uc3m_logistics.json_store.json_deliver_store import JsonDeliverStore

from uc3m_logistics.json_store.json_order_store import JsonOrderStore


class TestSigleton(TestCase):
    """Tests of singleton"""

    def test_singleton_order_manager(self):
        """Test if numerous OrderManager are equal"""
        om1 = OrderManager()
        om2 = OrderManager()
        om3 = OrderManager()
        self.assertEqual(om1, om2)
        self.assertEqual(om2, om3)
        self.assertEqual(om1, om3)

    def test_singleton_json_deliver_store(self):
        """Test if numerous JsonDeliverStore are equal """
        deliver1 = JsonDeliverStore()
        deliver2 = JsonDeliverStore()
        deliver3 = JsonDeliverStore()
        self.assertEqual(deliver1, deliver2)
        self.assertEqual(deliver1, deliver3)
        self.assertEqual(deliver2, deliver3)

    def test_singleton_json_order_store(self):
        """Test if numerous JsonOrderStore are equal"""
        os1 = JsonOrderStore()
        os2 = JsonOrderStore()
        os3 = JsonOrderStore()
        self.assertEqual(os1, os2)
        self.assertEqual(os2, os3)
        self.assertEqual(os1, os3)
