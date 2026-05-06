from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Order, SalesLog, Product
from schemas import SalesReport, TopProduct
from typing import List

class SalesAgent:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_orders(self, date: datetime = None):
        if not date:
            date = datetime.now()
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        orders = self.db.query(Order).filter(Order.created_at >= start, Order.created_at < end).all()
        return orders

    def get_daily_revenue(self, date: datetime = None):
        orders = self.get_daily_orders(date)
        return sum(order.total_amount for order in orders)

    def get_sales_report(self, period: str = "daily"):
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        orders = self.db.query(Order).filter(Order.created_at >= start).all()
        return SalesReport(
            total_orders=len(orders),
            total_revenue=sum(o.total_amount for o in orders),
            period=period
        )

    def get_top_selling_products(self, limit: int = 5) -> List[TopProduct]:
        from sqlalchemy import func
        results = (
            self.db.query(
                Product.name,
                func.sum(SalesLog.quantity).label("total_sold"),
                func.sum(SalesLog.revenue).label("total_revenue")
            )
            .join(SalesLog, Product.id == SalesLog.product_id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SalesLog.quantity).desc())
            .limit(limit)
            .all()
        )
        return [TopProduct(product_name=r[0], total_sold=r[1], total_revenue=r[2]) for r in results]

    def process_query(self, query: str) -> str:
        query_lower = query.lower()
        if "orders today" in query_lower or "daily orders" in query_lower:
            orders = self.get_daily_orders()
            revenue = self.get_daily_revenue()
            return f"Total orders today: {len(orders)}\nRevenue: ${revenue:.2f}"

        elif "revenue" in query_lower:
            report = self.get_sales_report("daily")
            return f"Daily revenue: ${report.total_revenue:.2f}"

        elif "top selling" in query_lower or "best product" in query_lower:
            top = self.get_top_selling_products(1)
            if top:
                return f"Best product: {top[0].product_name} ({top[0].total_sold} sold, ${top[0].total_revenue:.2f} revenue)"
            return "No sales data available"

        elif "report" in query_lower:
            report = self.get_sales_report("daily")
            return f"Daily Report:\nOrders: {report.total_orders}\nRevenue: ${report.total_revenue:.2f}"

        else:
            return "I can help with: daily orders, revenue, top selling products, and sales reports."
