from typing import List

from .models import Product, Order, Customer
from .repositories import ProductRepository, OrderRepository, CustomerRepository


class WarehouseService:
    def __init__(self, product_repo: ProductRepository, order_repo: OrderRepository, customer_repo: CustomerRepository):
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.customer_repo = customer_repo

    def create_product(self, name: str, quantity: int, price: float) -> Product:
        product = Product(id=None, name=name, quantity=quantity, price=price)
        self.product_repo.add(product)
        return product

    def create_order(self, products: List[Product]) -> Order:
        order = Order(id=None, products=products)
        self.order_repo.add(order)
        return order

    # Added create_customer
    def create_customer(self, name: str, email: str) -> Customer:
        customer = Customer(id=None, name=name, email=email)
        self.customer_repo.add(customer)
        return customer
