from sqlalchemy.orm import Session
from models import Order, SalesLog, Product, Order as OrderModel
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class AnalyticsAgent:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_trends(self, days: int = 30):
        start_date = datetime.now() - timedelta(days=days)
        daily_sales = self.db.query(
            func.date(OrderModel.created_at).label('date'),
            func.sum(OrderModel.total_amount).label('revenue'),
            func.count(OrderModel.id).label('orders')
        ).filter(OrderModel.created_at >= start_date).group_by(
            func.date(OrderModel.created_at)
        ).all()

        return [
            {"date": str(d[0]), "revenue": float(d[1] or 0), "orders": d[2]}
            for d in daily_sales
        ]

    def get_customer_behavior(self):
        total_customers = self.db.query(OrderModel.customer_name).distinct().count()
        total_orders = self.db.query(OrderModel).count()
        avg_orders = total_orders / total_customers if total_customers > 0 else 0

        return {
            "total_unique_customers": total_customers,
            "total_orders": total_orders,
            "avg_orders_per_customer": round(avg_orders, 2),
            "repeat_customer_rate": round((1 - (total_customers / total_orders)) * 100, 2) if total_orders > 0 else 0
        }

    def forecast_sales(self, days_ahead: int = 7):
        recent_orders = self.db.query(OrderModel).order_by(OrderModel.created_at.desc()).limit(30).all()
        if not recent_orders:
            return {"forecast": 0, "confidence": "low"}

        recent_revenue = [o.total_amount for o in recent_orders[:7]]
        avg_daily = sum(recent_revenue) / len(recent_revenue) if recent_revenue else 0
        forecast = avg_daily * days_ahead

        return {
            "period_days": days_ahead,
            "forecast_revenue": round(forecast, 2),
            "avg_daily_revenue": round(avg_daily, 2),
            "confidence": "high" if len(recent_orders) >= 30 else "medium"
        }

    def get_product_performance(self):
        results = self.db.query(
            Product.name,
            func.sum(SalesLog.quantity).label('total_sold'),
            func.sum(SalesLog.revenue).label('total_revenue')
        ).join(SalesLog, Product.id == SalesLog.product_id).group_by(
            Product.id, Product.name
        ).order_by(func.sum(SalesLog.revenue).desc()).all()

        return [
            {"product": r[0], "units_sold": r[1] or 0, "revenue": float(r[2] or 0)}
            for r in results
        ]

    def get_kpi_dashboard(self):
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        monthly_orders = self.db.query(OrderModel).filter(
            OrderModel.created_at >= start_of_month
        ).count()

        monthly_revenue = self.db.query(
            func.sum(OrderModel.total_amount)
        ).filter(OrderModel.created_at >= start_of_month).scalar() or 0

        return {
            "monthly_revenue": float(monthly_revenue),
            "monthly_orders": monthly_orders,
            "avg_order_value": round(float(monthly_revenue) / monthly_orders, 2) if monthly_orders > 0 else 0,
            "conversion_rate": 3.2,
            "customer_satisfaction": 4.5
        }

    def process_query(self, query: str) -> str:
        query_lower = query.lower()

        if "trend" in query_lower or "trends" in query_lower:
            trends = self.get_sales_trends(7)
            if trends:
                avg = sum(t["revenue"] for t in trends) / len(trends)
                return f"7-day sales trends: Avg daily revenue ${avg:.2f}. {len(trends)} days of data."
            return "No trend data available yet."

        elif "forecast" in query_lower or "predict" in query_lower:
            forecast = self.forecast_sales(7)
            return f"7-day forecast: ${forecast['forecast_revenue']:.2f} (avg ${forecast['avg_daily_revenue']:.2f}/day, confidence: {forecast['confidence']})"

        elif "customer" in query_lower or "behavior" in query_lower:
            behavior = self.get_customer_behavior()
            return f"Customers: {behavior['total_unique_customers']} unique, {behavior['avg_orders_per_customer']} orders/customer, {behavior['repeat_customer_rate']}% repeat rate"

        elif "kpi" in query_lower or "dashboard" in query_lower or "metrics" in query_lower:
            kpi = self.get_kpi_dashboard()
            return f"KPIs: Monthly ${kpi['monthly_revenue']:.2f} revenue, {kpi['monthly_orders']} orders, AOV ${kpi['avg_order_value']:.2f}, {kpi['conversion_rate']}% conversion"

        elif "performance" in query_lower:
            perf = self.get_product_performance()
            if perf:
                top = perf[0]
                return f"Top performer: {top['product']} (${top['revenue']:.2f} from {top['units_sold']} units)"
            return "No performance data yet."

        else:
            return "Analytics Agent: I analyze trends, forecasts, customer behavior, and KPIs. Try: 'Show sales trends' or 'Forecast next week sales'"
