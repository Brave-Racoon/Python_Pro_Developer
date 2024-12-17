from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ProductORM(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)


class OrderORM(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)

    order_product_assocoations = Table(
        'order_product_assocoations', Base.metadata,
        Column('order_id', ForeignKey('orders.id')),
        Column('product_id', ForeignKey('products.id'))
    )

    products = relationship("ProductORM", secondary=order_product_assocoations)


# Added CustomerORM
class CustomerORM(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
