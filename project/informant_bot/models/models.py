# models.py
# initialize alembic: alembic revision --autogenerate -m "Initial migration"
# populate initialization to db: alembic upgrade head

# Create migration: alembic revision -m "Name_of_migration"
# Run migration: alembic upgrade head
# Revert migration to 1 step: alembic downgrade -1
# Delete unnecessary migration:
# Info: alembic current or alembic history --verbose
# Back to beginning: alembic downgrade base

# I have SQLAlchemy DB model. Is that correct?
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship, declarative_base
import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    user_tg_id = Column(Integer, nullable=True)
    user_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    ins_date = Column(DateTime, default=datetime.datetime.utcnow)

    addresses = relationship('UserAddresses', back_populates='user')
    notifications = relationship('UserNotify', back_populates='user')

    def __repr__(self):
        return f"<User(user_id={self.id}, telegram_id={self.user_tg_id})>"


class UserAddresses(Base):
    __tablename__ = 'user_address'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    street = Column(Text, nullable=True)
    number = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # Assuming 'user_id' is the table name for User
    ins_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='addresses')

    def __repr__(self):
        return f"<UserAddresses(user_id={self.user_id}, street={self.street})>"


class UserNotify(Base):
    __tablename__ = 'user_notify'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    off_id = Column(Integer, ForeignKey('blackout.id', ondelete='CASCADE'), nullable=False)
    notify_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='notifications')
    blackout = relationship('Blackout', back_populates='notifications')

    def __repr__(self):
        return f"<UserNotify(user_id={self.user_id}, off_id={self.off_id})>"


class Street(Base):
    __tablename__ = 'street'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    city = Column(Text, nullable=True)
    street = Column(Text, nullable=True)
    ins_date = Column(DateTime, default=datetime.datetime.utcnow)

    addresses = relationship('Address', back_populates='street')

    def __repr__(self):
        return f"<Street(city={self.city}, street={self.street})>"


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    street_id = Column(Integer, ForeignKey('street.id', ondelete='CASCADE'), nullable=False)
    number_from = Column(Text, nullable=False)
    number_to = Column(Text, nullable=True)
    ins_date = Column(DateTime, default=datetime.datetime.utcnow)

    street = relationship('Street', back_populates='addresses')
    blackouts = relationship('Blackout', back_populates='address')

    def __repr__(self):
        return f"<Address(street_id={self.street_id}, number_from={self.number_from})>"


class Blackout(Base):
    __tablename__ = 'blackout'

    id = Column(Integer, primary_key=True)  # Automatically generated primary key
    blackout_day = Column(Date, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id', ondelete='CASCADE'), nullable=False)
    ins_date = Column(DateTime, default=datetime.datetime.utcnow)

    address = relationship('Address', back_populates='blackouts')
    notifications = relationship('UserNotify', back_populates='blackout')

    def __repr__(self):
        return f"<Blackout(blackout_day={self.blackout_day}, address_id={self.address_id})>"

    #Step 3: Create the Database Engine and Session
#You need to create a database engine and a session to interact with your PostgreSQL database:

#from sqlalchemy.orm import sessionmaker

# Replace with your own database URL
#DATABASE_URL = "postgresql://username:password@localhost/dbname"

#engine = create_engine(DATABASE_URL)
#Session = sessionmaker(bind=engine)
#session = Session()
#Step 4: Create the Tables
#You can create the tables in your PostgreSQL database by calling:

#Base.metadata.create_all(engine)
#Notes:
#Relationships: Make sure to define the back_populates in your SQLAlchemy models to establish relationships. Adjust the foreign key references according to your actual user table name 
#(auth_user is a common name for Django's User model).
#Data Types: SQLAlchemy data types might differ from Django. For example, Django's ImageField is represented as a String in SQLAlchemy.
#Auto Increment and Primary Key: In SQLAlchemy, if you define a column with primary_key=True, it will automatically be autoincremented unless specified otherwise.
#DateTime Defaults: The default for DateTime fields is set to the current UTC time using datetime.datetime.utcnow.
#This should give you a starting point for using SQLAlchemy with PostgreSQL based on your Django models. Adjust any specific configurations or additional relationships as needed for your application.
