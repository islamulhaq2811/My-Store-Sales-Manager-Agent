from sales_agent import SalesAgent
from support_agent import SupportAgent
from marketing_agent import MarketingAgent
from analytics_agent import AnalyticsAgent
from inventory_agent import InventoryAgent
from mystore_agent import MystoreAgent
from database import is_mystore_configured, get_mystore_session
from typing import Dict, Any

class MasterAgent:
    def __init__(self, db, mystore_db=None):
        self.db = db
        self.mystore_db = mystore_db
        self.mystore = MystoreAgent()
        self.agents = {
            "sales": SalesAgent(db, mystore_db),
            "support": SupportAgent(db),
            "marketing": MarketingAgent(db),
            "analytics": AnalyticsAgent(db, mystore_db),
            "inventory": InventoryAgent(db),
        }

    def classify_intent(self, query: str) -> str:
        query_lower = query.lower()

        high_priority = {
            "support": ["refund", "warranty", "delivery", "track", "return", "exchange", "complaint", "cancel"],
            "marketing": ["campaign", "promotion", "lead", "marketing", "advertise", "roi"],
            "inventory": ["restock", "reorder", "low stock", "warehouse", "supplier", "purchase order"],
            "analytics": ["forecast", "predict", "trend", "analytics", "kpi", "dashboard"],
            "mystore": ["sql:", "mystore", "ecommerce", "custom query"],
        }

        for intent, keywords in high_priority.items():
            if any(kw in query_lower for kw in keywords):
                return intent

        sales_keywords = [
            "order", "revenue", "sales", "sell", "income", "profit", "best product",
            "top selling", "report", "daily", "weekly", "monthly", "earnings", "money",
            "how much", "total", "summary", "performance", "goals", "target", "trend",
            "how many"
        ]
        support_keywords = [
            "faq", "help", "support", "status", "shipping", "broken", "damaged",
            "issue", "problem", "replace", "guarantee", "service"
        ]
        marketing_keywords = [
            "discount", "budget", "promo", "offer", "deal", "sales funnel", "conversion"
        ]
        analytics_keywords = [
            "metric", "behavior", "customer insight", "performance analysis", "data", "statistics"
        ]
        inventory_keywords = [
            "stock", "inventory", "alert", "item count", "storage", "supply"
        ]

        scores = {
            "sales": sum(1 for kw in sales_keywords if kw in query_lower),
            "support": sum(1 for kw in support_keywords if kw in query_lower),
            "marketing": sum(1 for kw in marketing_keywords if kw in query_lower),
            "analytics": sum(1 for kw in analytics_keywords if kw in query_lower),
            "inventory": sum(1 for kw in inventory_keywords if kw in query_lower),
        }

        best = max(scores, key=scores.get) if max(scores.values()) > 0 else "sales"
        return best

    def process(self, query: str) -> Dict[str, Any]:
        intent = self.classify_intent(query)
        if intent == "mystore":
            response = self.mystore.process_query(query)
            return {"response": response, "agent": "mystore", "timestamp": str(__import__('datetime').datetime.now())}

        agent = self.agents.get(intent)
        if not agent:
            return {"response": "No agent available for this request.", "agent": "none"}

        response = agent.process_query(query)
        return {"response": response, "agent": intent, "timestamp": str(__import__('datetime').datetime.now())}
