from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class RefundStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    processed = "processed"
    rejected = "rejected"

class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    customer_name = Column(String(100), nullable=False)
    reason = Column(Text)
    status = Column(Enum(RefundStatus), default=RefundStatus.pending)
    amount = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Warranty(Base):
    __tablename__ = "warranties"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer)
    customer_name = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    is_active = Column(Enum("active", "expired", "voided"), default="active")

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    tracking_number = Column(String(100))
    carrier = Column(String(50))
    status = Column(String(50), default="processing")
    estimated_delivery = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    campaign_type = Column(String(50))
    budget = Column(Float, default=0)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Promotion(Base):
    __tablename__ = "promotions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    discount_type = Column(String(20))
    discount_value = Column(Float)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    product_id = Column(Integer)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    source = Column(String(50))
    status = Column(String(20), default="new")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True)
    quantity_in_stock = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    warehouse_location = Column(String(50))
    last_restocked = Column(DateTime(timezone=True), server_default=func.now())

class StockAlert(Base):
    __tablename__ = "stock_alerts"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    alert_type = Column(String(50))
    message = Column(Text)
    is_resolved = Column(String(10), default="no")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float)
    total_amount = Column(Float)
    status = Column(String(20), default="pending")
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_delivery = Column(DateTime(timezone=True))
