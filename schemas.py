from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

class ProductCreate(BaseModel):
    name: str
    price: float
    category: Optional[str] = None

class ProductResponse(ProductCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_name: str
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    product_id: int
    quantity: int
    total_amount: float
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class SalesReport(BaseModel):
    total_orders: int
    total_revenue: float
    period: str

class TopProduct(BaseModel):
    product_name: str
    total_sold: int
    total_revenue: float

class RefundCreate(BaseModel):
    order_id: int
    customer_name: str
    reason: Optional[str] = None
    amount: Optional[float] = None

class RefundResponse(RefundCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class WarrantyCreate(BaseModel):
    order_id: int
    product_id: int
    customer_name: str

class WarrantyResponse(WarrantyCreate):
    id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: str
    class Config:
        from_attributes = True

class DeliveryCreate(BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: Optional[str] = "processing"
    estimated_delivery: Optional[datetime] = None

class DeliveryResponse(DeliveryCreate):
    id: int
    delivered_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# Marketing Schemas
class CampaignCreate(BaseModel):
    name: str
    campaign_type: Optional[str] = "email"
    budget: Optional[float] = 0
    end_date: Optional[str] = None
    description: Optional[str] = None

class CampaignResponse(CampaignCreate):
    id: int
    status: str
    start_date: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class PromotionCreate(BaseModel):
    name: str
    discount_type: str
    discount_value: float
    product_id: Optional[int] = None
    duration_days: Optional[int] = 30

class PromotionResponse(BaseModel):
    id: int
    name: str
    discount_type: str
    discount_value: float
    product_id: Optional[int] = None
    status: str
    start_date: datetime
    end_date: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "website"
    notes: Optional[str] = None

class LeadResponse(LeadCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True


# Inventory Schemas
class InventoryItemCreate(BaseModel):
    product_id: int
    quantity_in_stock: int
    reorder_point: Optional[int] = 10
    warehouse_location: Optional[str] = "Main"

class InventoryItemResponse(InventoryItemCreate):
    id: int
    last_restocked: datetime
    class Config:
        from_attributes = True

class StockAlertResponse(BaseModel):
    id: int
    product_id: int
    alert_type: str
    message: Optional[str] = None
    is_resolved: str
    created_at: datetime
    class Config:
        from_attributes = True

class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class SupplierResponse(SupplierCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    product_id: int
    quantity: int

class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    quantity: int
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    status: str
    order_date: datetime
    expected_delivery: Optional[datetime] = None
    class Config:
        from_attributes = True
