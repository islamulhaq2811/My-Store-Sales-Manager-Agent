from sqlalchemy.orm import Session
from models import InventoryItem, StockAlert, Supplier, PurchaseOrder
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any

class InventoryAgent:
    def __init__(self, db: Session):
        self.db = db

    def add_inventory_item(self, product_id: int, quantity: int, reorder_point: int = 10,
                           warehouse_location: str = "Main"):
        existing = self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        if existing:
            existing.quantity_in_stock = quantity
            existing.reorder_point = reorder_point
            existing.warehouse_location = warehouse_location
            existing.last_restocked = datetime.now()
        else:
            item = InventoryItem(
                product_id=product_id,
                quantity_in_stock=quantity,
                reorder_point=reorder_point,
                warehouse_location=warehouse_location
            )
            self.db.add(item)
        self.db.commit()
        return existing or item

    def update_stock(self, product_id: int, quantity_change: int):
        item = self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()
        if not item:
            return None
        item.quantity_in_stock += quantity_change
        item.last_restocked = datetime.now()
        self.db.commit()

        if item.quantity_in_stock <= item.reorder_point:
            self.create_stock_alert(product_id, "low_stock",
                                    f"Stock low: {item.quantity_in_stock} units remaining")
        return item

    def create_stock_alert(self, product_id: int, alert_type: str, message: str):
        alert = StockAlert(
            product_id=product_id,
            alert_type=alert_type,
            message=message
        )
        self.db.add(alert)
        self.db.commit()
        return alert

    def get_low_stock_items(self):
        items = self.db.query(InventoryItem).filter(
            InventoryItem.quantity_in_stock <= InventoryItem.reorder_point
        ).all()
        return items

    def get_inventory_status(self):
        total_items = self.db.query(InventoryItem).count()
        low_stock = self.db.query(InventoryItem).filter(
            InventoryItem.quantity_in_stock <= InventoryItem.reorder_point
        ).count()

        return {
            "total_products": total_items,
            "low_stock_count": low_stock,
            "stock_health": "Good" if low_stock == 0 else "Attention Needed"
        }

    def add_supplier(self, name: str, contact_name: str = None, email: str = None,
                     phone: str = None, address: str = None):
        supplier = Supplier(
            name=name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            address=address
        )
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def create_purchase_order(self, supplier_id: int, product_id: int, quantity: int):
        po = PurchaseOrder(
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=0,
            total_amount=0
        )
        self.db.add(po)
        self.db.commit()
        self.db.refresh(po)
        return po

    def get_alerts(self, unresolved_only: bool = True):
        query = self.db.query(StockAlert)
        if unresolved_only:
            query = query.filter(StockAlert.is_resolved == "no")
        return query.all()

    def process_query(self, query: str) -> str:
        query_lower = query.lower()

        if "stock" in query_lower or "inventory" in query_lower:
            status = self.get_inventory_status()
            return f"Inventory: {status['total_products']} products tracked. Status: {status['stock_health']}"

        elif "low stock" in query_lower or "reorder" in query_lower:
            items = self.get_low_stock_items()
            if items:
                item_list = [f"Product #{i.product_id}: {i.quantity_in_stock} units" for i in items[:3]]
                return f"Low stock alert: {'; '.join(item_list)}"
            return "All items are above reorder points."

        elif "alert" in query_lower:
            alerts = self.get_alerts(True)
            return f"Active alerts: {len(alerts)}. Check inventory for details."

        elif "supplier" in query_lower:
            suppliers = self.db.query(Supplier).all()
            return f"Suppliers: {len(suppliers)} registered. Latest: {suppliers[0].name if suppliers else 'None'}"

        elif "purchase order" in query_lower or "po" in query_lower:
            pos = self.db.query(PurchaseOrder).all()
            pending = [p for p in pos if p.status == "pending"]
            return f"Purchase Orders: {len(pos)} total, {len(pending)} pending."

        elif "value" in query_lower or "worth" in query_lower:
            return "Inventory value tracking is available through Mystore product prices."

        else:
            return "Inventory Agent: I track stock, alerts, suppliers, and purchase orders. Try: 'Check stock levels' or 'Show low stock items'"
