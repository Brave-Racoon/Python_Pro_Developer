# Added
import unittest
from unittest.mock import MagicMock
from domain.models import Product, Order, Customer
from domain.services import WarehouseService


class TestWarehouseService(unittest.TestCase):
    def setUp(self):
        self.product_repo = MagicMock()
        self.order_repo = MagicMock()
        self.customer_repo = MagicMock()
        self.service = WarehouseService(self.product_repo, self.order_repo, self.customer_repo)

    def test_create_product(self):
        product = self.service.create_product(name="Test Product", quantity=10, price=100.0)
        self.product_repo.add.assert_called_once()
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.quantity, 10)
        self.assertEqual(product.price, 100.0)

    def test_create_order(self):
        product = Product(id=1, name="Test Product", quantity=10, price=100.0)
        order = self.service.create_order(products=[product])
        self.order_repo.add.assert_called_once()
        self.assertEqual(len(order.products), 1)

    def test_create_customer(self):
        customer = self.service.create_customer(name="Test Customer", email="test@example.com")
        self.customer_repo.add.assert_called_once()
        self.assertEqual(customer.name, "Test Customer")
        self.assertEqual(customer.email, "test@example.com")


if __name__ == '__main__':
    unittest.main()
