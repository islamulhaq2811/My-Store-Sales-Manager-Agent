from sqlalchemy.orm import Session
from models import Refund, RefundStatus, Warranty, Delivery
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

    def create_refund_request(self, order_id: int, customer_name: str = "Customer", reason: str = "Requested via chat"):
        refund = Refund(
            order_id=order_id,
            customer_name=customer_name,
            reason=reason,
            amount=0,
            status=RefundStatus.pending
        )
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)
        return refund

    def create_warranty(self, order_id: int, product_id: int = None, customer_name: str = "Customer"):
        start = datetime.now()
        end = start + timedelta(days=365)
        warranty = Warranty(
            order_id=order_id,
            product_id=product_id,
            customer_name=customer_name,
            start_date=start,
            end_date=end,
            is_active="active"
        )
        self.db.add(warranty)
        self.db.commit()
        self.db.refresh(warranty)
        return warranty

    def create_delivery(self, order_id: int, carrier: str = "Standard", status: str = "processing"):
        delivery = Delivery(
            order_id=order_id,
            carrier=carrier,
            status=status,
            estimated_delivery=datetime.now() + timedelta(days=3)
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def process_query(self, query: str) -> str:
        query_lower = query.lower()
        order_id = self._extract_order_id(query)

        if "refund" in query_lower:
            existing = self.get_refund_status(order_id)
            if existing:
                r = existing[0]
                return f"Refund #{r.id} for Order #{r.order_id}: Status: {r.status.value}, Amount: ${r.amount or 0:.2f}, Reason: {r.reason or 'N/A'}"

            create_words = ["want", "request", "create", "make", "apply", "need", "please"]
            if any(w in query_lower for w in create_words) and order_id:
                customer = "Customer"
                refund = self.create_refund_request(order_id, customer)
                return f"✅ Refund request #{refund.id} created for Order #{order_id}. Status: Pending. We'll process it within 3-5 business days."
            return "To request a refund, say 'I want a refund for order [number]' and I'll create it for you."

        elif "warranty" in query_lower:
            existing = self.get_warranty_status(order_id)
            if existing:
                w = existing[0]
                return f"Warranty for Order #{w.order_id}: Status: {w.is_active}, Start: {w.start_date.date()}, End: {w.end_date.date() if w.end_date else 'N/A'}"

            create_words = ["want", "request", "create", "check", "need", "start", "register"]
            if any(w in query_lower for w in create_words) and order_id:
                warranty = self.create_warranty(order_id, customer_name="Customer")
                return f"✅ Warranty registered for Order #{order_id}. Covers 12 months from {warranty.start_date.date()}."
            return "To register a warranty, say 'Register warranty for order [number]'. Standard warranty covers 12 months."

        elif "delivery" in query_lower or "shipping" in query_lower or "track" in query_lower:
            if order_id:
                existing = self.get_delivery_status(order_id)
                if existing:
                    d = existing[0]
                    return f"Delivery for Order #{d.order_id}: Status: {d.status}, Carrier: {d.carrier or 'N/A'}, Tracking: {d.tracking_number or 'N/A'}, Estimated: {d.estimated_delivery.date() if d.estimated_delivery else 'N/A'}"

                create_words = ["want", "track", "check", "where", "status", "create"]
                if any(w in query_lower for w in create_words):
                    delivery = self.create_delivery(order_id)
                    return f"📦 Delivery created for Order #{order_id}. Status: {delivery.status}, Estimated delivery: {delivery.estimated_delivery.date()}. Standard delivery takes 2-3 business days."
            else:
                return "Please provide your order ID to track delivery, e.g., 'Track delivery for order 1'."
            return "Standard delivery takes 2-3 business days. Please provide your order ID to check status."

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
