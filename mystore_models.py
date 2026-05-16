from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

MystoreBase = declarative_base()

class MystoreProduct(MystoreBase):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    slug = Column(String(255))
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    image = Column(String(500))
    category = Column(String(100))
    rating = Column(DECIMAL(2, 1))
    reviews = Column(Integer)
    created_at = Column(DateTime)

class MystoreOrder(MystoreBase):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    payment_method = Column(String(50))
    card_number = Column(String(100))
    account_number = Column(String(100))
    cart_data = Column(Text)
    total_amount = Column(DECIMAL(10, 2))
    order_date = Column(DateTime)

class MystoreContact(MystoreBase):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))
    subject = Column(String(255))
    message = Column(Text)
    date = Column(DateTime)
