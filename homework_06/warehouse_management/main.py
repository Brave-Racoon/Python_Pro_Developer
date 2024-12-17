from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.services import WarehouseService
from infrastructure.orm import Base
from infrastructure.repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyCustomerRepository,
)
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def main():
    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    customer_repo = SqlAlchemyCustomerRepository(session)

    uow = SqlAlchemyUnitOfWork(session)

    warehouse_service = WarehouseService(product_repo, order_repo, customer_repo)
    with uow:
        new_product = warehouse_service.create_product(
            name="test1", quantity=1, price=100
        )
        uow.commit()
        print(f"create product: {new_product}")
        # Added create customer procedure
        new_customer = warehouse_service.create_customer(
            name="Customer", email="customer@example.com"
        )
        uow.commit()
        print(f"Created customer: {new_customer}")


if __name__ == "__main__":
    main()
