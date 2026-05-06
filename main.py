from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base
from master_agent import MasterAgent
from sales_agent import SalesAgent
from support_agent import SupportAgent
from marketing_agent import MarketingAgent
from analytics_agent import AnalyticsAgent
from inventory_agent import InventoryAgent
from schemas import (
    OrderCreate, OrderResponse, ProductCreate, ProductResponse, SalesReport,
    RefundCreate, RefundResponse, WarrantyCreate, WarrantyResponse,
    DeliveryCreate, DeliveryResponse,
    CampaignCreate, CampaignResponse, PromotionCreate, PromotionResponse,
    LeadCreate, LeadResponse, InventoryItemCreate, InventoryItemResponse,
    StockAlertResponse, SupplierCreate, SupplierResponse,
    PurchaseOrderCreate, PurchaseOrderResponse
)
from auth import verify_api_key
from datetime import datetime
from typing import List

app = FastAPI(title="Sales Manager Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Sales Manager Agent is running"}

@app.post("/chat", dependencies=[Depends(verify_api_key)])
def chat(query: dict, db: Session = Depends(get_db)):
    master = MasterAgent(db)
    result = master.process(query.get("query", ""))
    return result

@app.post("/products", response_model=ProductResponse, dependencies=[Depends(verify_api_key)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    from models import Product
    db_product = Product(name=product.name, price=product.price, category=product.category)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=List[ProductResponse], dependencies=[Depends(verify_api_key)])
def list_products(db: Session = Depends(get_db)):
    from models import Product
    return db.query(Product).all()

@app.post("/orders", response_model=OrderResponse, dependencies=[Depends(verify_api_key)])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    from models import Product, Order, SalesLog
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    total = product.price * order.quantity
    db_order = Order(
        customer_name=order.customer_name,
        product_id=order.product_id,
        quantity=order.quantity,
        total_amount=total,
        status="completed"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    sales_log = SalesLog(
        order_id=db_order.id,
        product_id=order.product_id,
        quantity=order.quantity,
        revenue=total
    )
    db.add(sales_log)
    db.commit()
    return db_order

@app.get("/orders/today", dependencies=[Depends(verify_api_key)])
def orders_today(db: Session = Depends(get_db)):
    agent = SalesAgent(db)
    orders = agent.get_daily_orders()
    return {"count": len(orders), "orders": orders}

@app.get("/sales/report", dependencies=[Depends(verify_api_key)])
def sales_report(period: str = "daily", db: Session = Depends(get_db)):
    agent = SalesAgent(db)
    return agent.get_sales_report(period)

@app.get("/sales/top-products", dependencies=[Depends(verify_api_key)])
def top_products(limit: int = 5, db: Session = Depends(get_db)):
    agent = SalesAgent(db)
    return agent.get_top_selling_products(limit)

# Support Agent Endpoints
@app.post("/refunds", response_model=RefundResponse, dependencies=[Depends(verify_api_key)])
def create_refund(refund: RefundCreate, db: Session = Depends(get_db)):
    from models import Refund, RefundStatus
    db_refund = Refund(
        order_id=refund.order_id,
        customer_name=refund.customer_name,
        reason=refund.reason,
        amount=refund.amount,
        status=RefundStatus.pending
    )
    db.add(db_refund)
    db.commit()
    db.refresh(db_refund)
    return db_refund

@app.get("/refunds", response_model=List[RefundResponse], dependencies=[Depends(verify_api_key)])
def list_refunds(order_id: int = None, db: Session = Depends(get_db)):
    from models import Refund
    query = db.query(Refund)
    if order_id:
        query = query.filter(Refund.order_id == order_id)
    return query.all()

@app.post("/warranties", response_model=WarrantyResponse, dependencies=[Depends(verify_api_key)])
def create_warranty(warranty: WarrantyCreate, db: Session = Depends(get_db)):
    from models import Warranty
    from datetime import timedelta
    start = datetime.now()
    end = start + timedelta(days=365)
    db_warranty = Warranty(
        order_id=warranty.order_id,
        product_id=warranty.product_id,
        customer_name=warranty.customer_name,
        start_date=start,
        end_date=end,
        is_active="active"
    )
    db.add(db_warranty)
    db.commit()
    db.refresh(db_warranty)
    return db_warranty

@app.get("/warranties", response_model=List[WarrantyResponse], dependencies=[Depends(verify_api_key)])
def list_warranties(order_id: int = None, db: Session = Depends(get_db)):
    from models import Warranty
    query = db.query(Warranty)
    if order_id:
        query = query.filter(Warranty.order_id == order_id)
    return query.all()

@app.post("/deliveries", response_model=DeliveryResponse, dependencies=[Depends(verify_api_key)])
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    from models import Delivery
    db_delivery = Delivery(
        order_id=delivery.order_id,
        tracking_number=delivery.tracking_number,
        carrier=delivery.carrier,
        status=delivery.status,
        estimated_delivery=delivery.estimated_delivery
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

@app.get("/deliveries", response_model=List[DeliveryResponse], dependencies=[Depends(verify_api_key)])
def list_deliveries(order_id: int = None, db: Session = Depends(get_db)):
    from models import Delivery
    query = db.query(Delivery)
    if order_id:
        query = query.filter(Delivery.order_id == order_id)
    return query.all()

# Marketing Agent Endpoints
@app.post("/marketing/campaigns", response_model=CampaignResponse, dependencies=[Depends(verify_api_key)])
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    end_date = datetime.fromisoformat(campaign.end_date) if campaign.end_date else None
    result = agent.create_campaign(campaign.name, campaign.campaign_type, campaign.budget, end_date, campaign.description)
    return result

@app.get("/marketing/campaigns", dependencies=[Depends(verify_api_key)])
def list_campaigns(status: str = "active", db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_campaigns(status)

@app.post("/marketing/promotions", response_model=PromotionResponse, dependencies=[Depends(verify_api_key)])
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    result = agent.create_promotion(promotion.name, promotion.discount_type, promotion.discount_value, promotion.product_id, promotion.duration_days)
    return result

@app.get("/marketing/promotions", dependencies=[Depends(verify_api_key)])
def list_promotions(status: str = "active", db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_promotions(status)

@app.post("/marketing/leads", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
def add_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    result = agent.add_lead(lead.name, lead.email, lead.phone, lead.source, lead.notes)
    return result

@app.get("/marketing/leads", dependencies=[Depends(verify_api_key)])
def list_leads(status: str = None, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_leads(status)

@app.get("/marketing/performance", dependencies=[Depends(verify_api_key)])
def campaign_performance(campaign_id: int = None, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_campaign_performance(campaign_id)

# Analytics Agent Endpoints
@app.get("/analytics/trends", dependencies=[Depends(verify_api_key)])
def sales_trends(days: int = 30, db: Session = Depends(get_db)):
    agent = AnalyticsAgent(db)
    return agent.get_sales_trends(days)

@app.get("/analytics/forecast", dependencies=[Depends(verify_api_key)])
def forecast_sales(days_ahead: int = 7, db: Session = Depends(get_db)):
    agent = AnalyticsAgent(db)
    return agent.forecast_sales(days_ahead)

@app.get("/analytics/customer-behavior", dependencies=[Depends(verify_api_key)])
def customer_behavior(db: Session = Depends(get_db)):
    agent = AnalyticsAgent(db)
    return agent.get_customer_behavior()

@app.get("/analytics/product-performance", dependencies=[Depends(verify_api_key)])
def product_performance(db: Session = Depends(get_db)):
    agent = AnalyticsAgent(db)
    return agent.get_product_performance()

@app.get("/analytics/kpi", dependencies=[Depends(verify_api_key)])
def kpi_dashboard(db: Session = Depends(get_db)):
    agent = AnalyticsAgent(db)
    return agent.get_kpi_dashboard()

# Inventory Agent Endpoints
@app.post("/inventory/items", response_model=InventoryItemResponse, dependencies=[Depends(verify_api_key)])
def add_inventory(item: InventoryItemCreate, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    result = agent.add_inventory_item(item.product_id, item.quantity_in_stock, item.reorder_point, item.warehouse_location)
    return result

@app.get("/inventory/items", dependencies=[Depends(verify_api_key)])
def get_inventory_status(db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.get_inventory_status()

@app.get("/inventory/low-stock", dependencies=[Depends(verify_api_key)])
def low_stock_items(db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.get_low_stock_items()

@app.post("/inventory/stock/update", dependencies=[Depends(verify_api_key)])
def update_stock(product_id: int, quantity_change: int, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    result = agent.update_stock(product_id, quantity_change)
    return result

@app.post("/inventory/suppliers", response_model=SupplierResponse, dependencies=[Depends(verify_api_key)])
def add_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    result = agent.add_supplier(supplier.name, supplier.contact_name, supplier.email, supplier.phone, supplier.address)
    return result

@app.get("/inventory/suppliers", dependencies=[Depends(verify_api_key)])
def list_suppliers(db: Session = Depends(get_db)):
    from models import Supplier
    return db.query(Supplier).all()

@app.post("/inventory/purchase-orders", response_model=PurchaseOrderResponse, dependencies=[Depends(verify_api_key)])
def create_po(po: PurchaseOrderCreate, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    result = agent.create_purchase_order(po.supplier_id, po.product_id, po.quantity)
    return result

@app.get("/inventory/purchase-orders", dependencies=[Depends(verify_api_key)])
def list_purchase_orders(db: Session = Depends(get_db)):
    from models import PurchaseOrder
    return db.query(PurchaseOrder).all()

@app.get("/inventory/alerts", dependencies=[Depends(verify_api_key)])
def get_alerts(unresolved_only: bool = True, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.get_alerts(unresolved_only)
