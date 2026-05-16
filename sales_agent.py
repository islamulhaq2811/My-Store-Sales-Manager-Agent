from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from mystore_models import MystoreProduct, MystoreOrder

class SalesAgent:
    def __init__(self, db: Session, mystore_db: Session = None):
        self.db = db
        self.mystore_db = mystore_db

    def get_daily_orders(self, date: datetime = None):
        if not self.mystore_db:
            return []
        if not date:
            date = datetime.now()
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        orders = self.mystore_db.query(MystoreOrder).filter(
            MystoreOrder.order_date >= start,
            MystoreOrder.order_date < end
        ).all()
        return orders

    def get_daily_revenue(self, date: datetime = None):
        orders = self.get_daily_orders(date)
        return sum(float(o.total_amount or 0) for o in orders)

    def get_sales_report(self, period: str = "daily"):
        if not self.mystore_db:
            return {"total_orders": 0, "total_revenue": 0, "period": period, "source": "no_mystore_data"}
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        orders = self.mystore_db.query(MystoreOrder).filter(
            MystoreOrder.order_date >= start
        ).all()

        return {
            "total_orders": len(orders),
            "total_revenue": sum(float(o.total_amount or 0) for o in orders),
            "period": period,
            "source": "mystore"
        }

    def get_top_selling_products(self, limit: int = 5):
        if not self.mystore_db:
            return []
        products = self.mystore_db.query(MystoreProduct).order_by(
            MystoreProduct.reviews.desc()
        ).limit(limit).all()
        return [{
            "product_name": p.name,
            "price": float(p.price or 0),
            "rating": float(p.rating or 0),
            "reviews": p.reviews or 0,
            "category": p.category
        } for p in products]

    def create_product(self, name: str, price: float, category: str = None, description: str = "", image: str = ""):
        if not self.mystore_db:
            return None
        import re
        slug = name.lower().replace(" ", "-")
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        product = MystoreProduct(
            name=name,
            slug=slug,
            price=price,
            category=category,
            description=description,
            image=image,
            rating=0,
            reviews=0,
            created_at=datetime.now()
        )
        self.mystore_db.add(product)
        self.mystore_db.commit()
        self.mystore_db.refresh(product)
        return product

    def list_products(self):
        if not self.mystore_db:
            return []
        return self.mystore_db.query(MystoreProduct).order_by(MystoreProduct.created_at.desc()).all()

    def get_product(self, product_id: int):
        if not self.mystore_db:
            return None
        return self.mystore_db.query(MystoreProduct).filter(MystoreProduct.id == product_id).first()

    def update_product(self, product_id: int, **kwargs):
        if not self.mystore_db:
            return None
        product = self.mystore_db.query(MystoreProduct).filter(MystoreProduct.id == product_id).first()
        if not product:
            return None
        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)
        self.mystore_db.commit()
        self.mystore_db.refresh(product)
        return product

    def delete_product(self, product_id: int):
        if not self.mystore_db:
            return False
        product = self.mystore_db.query(MystoreProduct).filter(MystoreProduct.id == product_id).first()
        if not product:
            return False
        self.mystore_db.delete(product)
        self.mystore_db.commit()
        return True

    def parse_cart_data(self, order):
        try:
            return json.loads(order.cart_data) if order.cart_data else []
        except (json.JSONDecodeError, TypeError):
            return []

    def process_query(self, query: str) -> str:
        query_lower = query.lower()
        if not self.mystore_db:
            return "Mystore database not connected. Please configure MYSTORE_DB in .env"

        if "orders today" in query_lower or "daily orders" in query_lower:
            orders = self.get_daily_orders()
            revenue = self.get_daily_revenue()
            return f"Total orders today: {len(orders)}\nRevenue: ${revenue:.2f}\nSource: Mystore"

        elif "revenue" in query_lower:
            report = self.get_sales_report("daily")
            return f"Daily revenue: ${report['total_revenue']:.2f}"

        elif "top selling" in query_lower or "best product" in query_lower:
            top = self.get_top_selling_products(1)
            if top:
                p = top[0]
                return f"Best product: {p['product_name']} (${p['price']:.2f}, {p['reviews']} reviews, rating: {p['rating']})"
            return "No products found in your store"

        elif "report" in query_lower:
            report = self.get_sales_report("daily")
            return f"Daily Report (Mystore):\nOrders: {report['total_orders']}\nRevenue: ${report['total_revenue']:.2f}"

        else:
            return "I can help with: daily orders, revenue, top selling products, and sales reports from your Mystore."
