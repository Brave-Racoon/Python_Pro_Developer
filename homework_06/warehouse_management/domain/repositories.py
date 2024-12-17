from abc import ABC, abstractmethod
from typing import List
from .models import Product, Order, Customer


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        pass

    @abstractmethod
    def get(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def list(self) -> List[Product]:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order):
        pass

    @abstractmethod
    def get(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def list(self) -> List[Order]:
        pass


# Added Customer Repository
class CustomerRepository(ABC):
    @abstractmethod
    def add(self, customer: Customer):
        pass

    @abstractmethod
    def get(self, customer_id: int) -> Customer:
        pass

    @abstractmethod
    def list(self) -> List[Customer]:
        pass
