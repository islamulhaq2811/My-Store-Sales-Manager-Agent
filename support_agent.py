from sqlalchemy.orm import Session
from models import Refund, RefundStatus, Warranty, Delivery, Order
from datetime import datetime, timedelta
from typing import Dict, Any

class SupportAgent:
    def __init__(self, db: Session):
        self.db = db

    def get_refund_status(self, order_id: int = None, customer_name: str = None):
        query = self.db.query(Refund)
        if order_id:
            query = query.filter(Refund.order_id == order_id)
        if customer_name:
            query = query.filter(Refund.customer_name.ilike(f"%{customer_name}%"))
        return query.all()

    def get_warranty_status(self, order_id: int = None, customer_name: str = None):
        query = self.db.query(Warranty)
        if order_id:
            query = query.filter(Warranty.order_id == order_id)
        if customer_name:
            query = query.filter(Warranty.customer_name.ilike(f"%{customer_name}%"))
        return query.all()

    def get_delivery_status(self, order_id: int = None, tracking_number: str = None):
        query = self.db.query(Delivery)
        if order_id:
            query = query.filter(Delivery.order_id == order_id)
        if tracking_number:
            query = query.filter(Delivery.tracking_number == tracking_number)
        return query.all()

    def process_query(self, query: str) -> str:
        query_lower = query.lower()

        if "refund" in query_lower:
            order_id = self._extract_order_id(query)
            refunds = self.get_refund_status(order_id)
            if refunds:
                r = refunds[0]
                return f"Refund #{r.id} for Order #{r.order_id}: Status: {r.status.value}, Amount: ${r.amount or 0:.2f}, Reason: {r.reason or 'N/A'}"
            return "No refund found. To request a refund, please provide your order ID. Refunds are processed within 3-5 business days."

        elif "warranty" in query_lower:
            order_id = self._extract_order_id(query)
            warranties = self.get_warranty_status(order_id)
            if warranties:
                w = warranties[0]
                return f"Warranty for Order #{w.order_id}: Status: {w.is_active}, Start: {w.start_date.date()}, End: {w.end_date.date() if w.end_date else 'N/A'}"
            return "No warranty found. Our standard warranty covers 12 months from purchase date. Please provide your order ID."

        elif "delivery" in query_lower or "shipping" in query_lower or "track" in query_lower:
            order_id = self._extract_order_id(query)
            deliveries = self.get_delivery_status(order_id)
            if deliveries:
                d = deliveries[0]
                return f"Delivery for Order #{d.order_id}: Status: {d.status}, Carrier: {d.carrier or 'N/A'}, Tracking: {d.tracking_number or 'N/A'}, Estimated: {d.estimated_delivery.date() if d.estimated_delivery else 'N/A'}"
            return "No delivery found. Standard delivery takes 2-3 business days. Please provide your order ID to track."

        elif "faq" in query_lower or "help" in query_lower:
            return "FAQs:\n1. How to track order? Use your order ID.\n2. Refund policy? 30-day money back.\n3. Warranty? 12 months standard.\n4. Delivery? 2-3 business days standard."

        else:
            return "Support Agent: How can I help you today? I handle refunds, warranties, delivery status, and FAQs. Please provide your order ID for specific inquiries."

    def _extract_order_id(self, query: str) -> int:
        import re
        match = re.search(r'order\s*#?\s*(\d+)', query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
