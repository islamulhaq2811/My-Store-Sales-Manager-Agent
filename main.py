from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, mystore_session_scope, is_mystore_configured, get_mystore_session
from models import Base
from mystore_models import MystoreProduct, MystoreOrder
from master_agent import MasterAgent
from sales_agent import SalesAgent
from support_agent import SupportAgent
from marketing_agent import MarketingAgent
from analytics_agent import AnalyticsAgent
from inventory_agent import InventoryAgent
from mystore_agent import MystoreAgent
from schemas import (
    RefundCreate, RefundResponse, WarrantyCreate, WarrantyResponse,
    DeliveryCreate, DeliveryResponse,
    CampaignCreate, CampaignResponse, PromotionCreate, PromotionResponse,
    LeadCreate, LeadResponse, InventoryItemCreate, InventoryItemResponse,
    StockAlertResponse, SupplierCreate, SupplierResponse,
    PurchaseOrderCreate, PurchaseOrderResponse
)
from auth import verify_api_key
from mystore_db import get_mystore_tables, get_table_columns
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Sales Manager Agent - Mystore Control", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

class MystoreProductCreate(BaseModel):
    name: str
    price: float
    category: Optional[str] = None
    description: Optional[str] = ""
    image: Optional[str] = ""

class MystoreProductOut(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    created_at: Optional[datetime] = None

class MystoreProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Sales Manager Agent is running", "mode": "mystore_control"}

@app.post("/chat", dependencies=[Depends(verify_api_key)])
def chat(query: dict, db: Session = Depends(get_db)):
    with mystore_session_scope() as mystore_db:
        master = MasterAgent(db, mystore_db)
        result = master.process(query.get("query", ""))
    return result

@app.post("/products", dependencies=[Depends(verify_api_key)])
def create_product(product: MystoreProductCreate):
    if not is_mystore_configured():
        raise HTTPException(status_code=400, detail="Mystore not configured")
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        result = agent.create_product(
            name=product.name, price=product.price,
            category=product.category, description=product.description, image=product.image
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create product")
        return {"id": result.id, "name": result.name, "price": float(result.price),
                "slug": result.slug, "category": result.category,
                "description": result.description, "image": result.image,
                "created_at": result.created_at.isoformat() if result.created_at else None}

@app.get("/products", dependencies=[Depends(verify_api_key)])
def list_products():
    if not is_mystore_configured():
        return []
    with mystore_session_scope() as mystore_db:
        products = mystore_db.query(MystoreProduct).order_by(MystoreProduct.created_at.desc()).all()
        result = []
        for p in products:
            result.append({"id": p.id, "name": p.name, "price": float(p.price or 0),
                          "slug": p.slug, "category": p.category, "description": p.description,
                          "image": p.image, "rating": float(p.rating or 0) if p.rating else None,
                          "reviews": p.reviews,
                          "created_at": p.created_at.isoformat() if p.created_at else None})
    return result

@app.get("/products/{product_id}", dependencies=[Depends(verify_api_key)])
def get_product(product_id: int):
    if not is_mystore_configured():
        raise HTTPException(status_code=400, detail="Mystore not configured")
    with mystore_session_scope() as mystore_db:
        product = mystore_db.query(MystoreProduct).filter(MystoreProduct.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", dependencies=[Depends(verify_api_key)])
def update_product(product_id: int, product: MystoreProductUpdate):
    if not is_mystore_configured():
        raise HTTPException(status_code=400, detail="Mystore not configured")
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        result = agent.update_product(product_id, **product.model_dump(exclude_none=True))
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
    return result

@app.delete("/products/{product_id}", dependencies=[Depends(verify_api_key)])
def delete_product(product_id: int):
    if not is_mystore_configured():
        raise HTTPException(status_code=400, detail="Mystore not configured")
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        success = agent.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.get("/orders", dependencies=[Depends(verify_api_key)])
def list_orders(limit: int = 50):
    if not is_mystore_configured():
        return []
    with mystore_session_scope() as mystore_db:
        orders = mystore_db.query(MystoreOrder).order_by(MystoreOrder.order_date.desc()).limit(limit).all()
        result = []
        for o in orders:
            result.append({"id": o.id, "customer_name": o.customer_name,
                          "total_amount": float(o.total_amount or 0),
                          "payment_method": o.payment_method,
                          "order_date": o.order_date.isoformat() if o.order_date else None})
    return result

@app.get("/orders/today", dependencies=[Depends(verify_api_key)])
def orders_today():
    if not is_mystore_configured():
        return {"count": 0, "orders": []}
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        orders = agent.get_daily_orders()
        result = []
        for o in orders:
            result.append({"id": o.id, "customer_name": o.customer_name,
                          "total_amount": float(o.total_amount or 0),
                          "order_date": o.order_date.isoformat() if o.order_date else None})
    return {"count": len(result), "orders": result, "source": "mystore"}

@app.get("/sales/report", dependencies=[Depends(verify_api_key)])
def sales_report(period: str = "daily"):
    if not is_mystore_configured():
        return {"total_orders": 0, "total_revenue": 0, "period": period}
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        return agent.get_sales_report(period)

@app.get("/sales/top-products", dependencies=[Depends(verify_api_key)])
def top_products(limit: int = 5):
    if not is_mystore_configured():
        return []
    with mystore_session_scope() as mystore_db:
        agent = SalesAgent(None, mystore_db)
        return agent.get_top_selling_products(limit)

@app.post("/refunds", response_model=RefundResponse, dependencies=[Depends(verify_api_key)])
def create_refund(refund: RefundCreate, db: Session = Depends(get_db)):
    from models import Refund, RefundStatus
    db_refund = Refund(order_id=refund.order_id, customer_name=refund.customer_name,
                       reason=refund.reason, amount=refund.amount, status=RefundStatus.pending)
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
    db_warranty = Warranty(order_id=warranty.order_id, product_id=warranty.product_id,
                           customer_name=warranty.customer_name, start_date=start, end_date=end, is_active="active")
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
    db_delivery = Delivery(order_id=delivery.order_id, tracking_number=delivery.tracking_number,
                           carrier=delivery.carrier, status=delivery.status,
                           estimated_delivery=delivery.estimated_delivery)
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

@app.post("/marketing/campaigns", response_model=CampaignResponse, dependencies=[Depends(verify_api_key)])
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    end_date = datetime.fromisoformat(campaign.end_date) if campaign.end_date else None
    return agent.create_campaign(campaign.name, campaign.campaign_type, campaign.budget, end_date, campaign.description)

@app.get("/marketing/campaigns", dependencies=[Depends(verify_api_key)])
def list_campaigns(status: str = "active", db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_campaigns(status)

@app.post("/marketing/promotions", response_model=PromotionResponse, dependencies=[Depends(verify_api_key)])
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.create_promotion(promotion.name, promotion.discount_type, promotion.discount_value, promotion.product_id, promotion.duration_days)

@app.get("/marketing/promotions", dependencies=[Depends(verify_api_key)])
def list_promotions(status: str = "active", db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_promotions(status)

@app.post("/marketing/leads", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
def add_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.add_lead(lead.name, lead.email, lead.phone, lead.source, lead.notes)

@app.get("/marketing/leads", dependencies=[Depends(verify_api_key)])
def list_leads(status: str = None, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_leads(status)

@app.get("/marketing/performance", dependencies=[Depends(verify_api_key)])
def campaign_performance(campaign_id: int = None, db: Session = Depends(get_db)):
    agent = MarketingAgent(db)
    return agent.get_campaign_performance(campaign_id)

@app.get("/analytics/trends", dependencies=[Depends(verify_api_key)])
def sales_trends(days: int = 30):
    if not is_mystore_configured():
        return []
    with mystore_session_scope() as mystore_db:
        agent = AnalyticsAgent(None, mystore_db)
        return agent.get_sales_trends(days)

@app.get("/analytics/forecast", dependencies=[Depends(verify_api_key)])
def forecast_sales(days_ahead: int = 7):
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    with mystore_session_scope() as mystore_db:
        agent = AnalyticsAgent(None, mystore_db)
        return agent.forecast_sales(days_ahead)

@app.get("/analytics/customer-behavior", dependencies=[Depends(verify_api_key)])
def customer_behavior():
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    with mystore_session_scope() as mystore_db:
        agent = AnalyticsAgent(None, mystore_db)
        return agent.get_customer_behavior()

@app.get("/analytics/product-performance", dependencies=[Depends(verify_api_key)])
def product_performance():
    if not is_mystore_configured():
        return []
    with mystore_session_scope() as mystore_db:
        agent = AnalyticsAgent(None, mystore_db)
        return agent.get_product_performance()

@app.get("/analytics/kpi", dependencies=[Depends(verify_api_key)])
def kpi_dashboard():
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    with mystore_session_scope() as mystore_db:
        agent = AnalyticsAgent(None, mystore_db)
        return agent.get_kpi_dashboard()

@app.post("/inventory/items", response_model=InventoryItemResponse, dependencies=[Depends(verify_api_key)])
def add_inventory(item: InventoryItemCreate, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.add_inventory_item(item.product_id, item.quantity_in_stock, item.reorder_point, item.warehouse_location)

@app.get("/inventory/items", dependencies=[Depends(verify_api_key)])
def get_inventory_status():
    if not is_mystore_configured():
        return {"total_products": 0, "low_stock_count": 0, "stock_health": "No Data"}
    with mystore_session_scope() as mystore_db:
        total = mystore_db.query(MystoreProduct).count()
        return {"total_products": total, "source": "mystore"}

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
    return agent.add_supplier(supplier.name, supplier.contact_name, supplier.email, supplier.phone, supplier.address)

@app.get("/inventory/suppliers", dependencies=[Depends(verify_api_key)])
def list_suppliers(db: Session = Depends(get_db)):
    from models import Supplier
    return db.query(Supplier).all()

@app.post("/inventory/purchase-orders", response_model=PurchaseOrderResponse, dependencies=[Depends(verify_api_key)])
def create_po(po: PurchaseOrderCreate, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.create_purchase_order(po.supplier_id, po.product_id, po.quantity)

@app.get("/inventory/purchase-orders", dependencies=[Depends(verify_api_key)])
def list_purchase_orders(db: Session = Depends(get_db)):
    from models import PurchaseOrder
    return db.query(PurchaseOrder).all()

@app.get("/inventory/alerts", dependencies=[Depends(verify_api_key)])
def get_alerts(unresolved_only: bool = True, db: Session = Depends(get_db)):
    agent = InventoryAgent(db)
    return agent.get_alerts(unresolved_only)

@app.get("/mystore/status")
def mystore_status():
    return {"configured": is_mystore_configured(),
            "tables": get_mystore_tables() if is_mystore_configured() else []}

@app.get("/mystore/tables")
def mystore_tables():
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    return {"tables": get_mystore_tables()}

@app.get("/mystore/tables/{table_name}")
def mystore_table_schema(table_name: str):
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    columns = get_table_columns(table_name)
    return {"table": table_name, "columns": columns}

@app.get("/mystore/data/{table_name}")
def mystore_table_data(table_name: str, limit: int = 50):
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    agent = MystoreAgent()
    return agent.get_table_data(table_name, limit)

@app.get("/mystore/stats")
def mystore_stats():
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    agent = MystoreAgent()
    stats = agent.get_store_stats()
    total_records = sum(s["record_count"] for s in stats.values()) if stats else 0
    return {"stats": stats, "total_records": total_records}

@app.post("/mystore/query")
def mystore_query(sql: dict):
    if not is_mystore_configured():
        return {"error": "Mystore not configured"}
    agent = MystoreAgent()
    query = sql.get("query", "")
    if agent.is_sql_query(query):
        result = agent.execute_raw_query(query)
        return result
    response = agent.process_query(query)
    return {"response": response}
