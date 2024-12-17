# Added
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.orm import Base, ProductORM, OrderORM, CustomerORM
from infrastructure.database import DATABASE_URL


class TestORM(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_product_orm(self):
        product = ProductORM(name="Test Product", quantity=10, price=100.0)
        self.session.add(product)
        self.session.commit()
        retrieved_product = self.session.query(ProductORM).filter_by(name="Test Product").one()
        self.assertEqual(retrieved_product.name, "Test Product")
        self.assertEqual(retrieved_product.quantity, 10)
        self.assertEqual(retrieved_product.price, 100.0)

    def test_customer_orm(self):
        customer = CustomerORM(name="Test Customer", email="test@example.com")
        self.session.add(customer)
        self.session.commit()
        retrieved_customer = self.session.query(CustomerORM).filter_by(name="Test Customer").one()
        self.assertEqual(retrieved_customer.name, "Test Customer")
        self.assertEqual(retrieved_customer.email, "test@example.com")


if __name__ == '__main__':
    unittest.main()
