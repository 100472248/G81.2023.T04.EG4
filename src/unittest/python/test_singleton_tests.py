"""Module for testing singleton"""
from unittest import TestCase
from uc3m_logistics import OrderManager


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
