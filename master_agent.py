from sales_agent import SalesAgent
from support_agent import SupportAgent
from marketing_agent import MarketingAgent
from analytics_agent import AnalyticsAgent
from inventory_agent import InventoryAgent
from typing import Dict, Any

class MasterAgent:
    def __init__(self, db):
        self.db = db
        self.agents = {
            "sales": SalesAgent(db),
            "support": SupportAgent(db),
            "marketing": MarketingAgent(db),
            "analytics": AnalyticsAgent(db),
            "inventory": InventoryAgent(db),
        }

    def classify_intent(self, query: str) -> str:
        query_lower = query.lower()
        sales_keywords = [
            "order", "revenue", "sales", "sell", "income", "profit", "best product",
            "top selling", "report", "daily", "weekly", "monthly", "earnings", "money",
            "how much", "total", "summary", "performance", "goals", "target", "trend"
        ]
        support_keywords = [
            "complaint", "refund", "warranty", "faq", "help", "support", "delivery",
            "status", "track", "shipping", "return", "exchange", "broken", "damaged",
            "issue", "problem", "cancel", "replace", "guarantee", "service"
        ]
        marketing_keywords = [
            "campaign", "promotion", "discount", "lead", "marketing", "advertise",
            "roi", "budget", "promo", "offer", "deal", "sales funnel", "conversion"
        ]
        analytics_keywords = [
            "forecast", "predict", "trend", "analytics", "kpi", "dashboard", "metric",
            "behavior", "customer insight", "performance analysis", "data", "statistics"
        ]
        inventory_keywords = [
            "stock", "inventory", "warehouse", "supplier", "purchase order", "reorder",
            "low stock", "restock", "alert", "item count", "storage", "supply"
        ]

        scores = {
            "sales": sum(1 for kw in sales_keywords if kw in query_lower),
            "support": sum(1 for kw in support_keywords if kw in query_lower),
            "marketing": sum(1 for kw in marketing_keywords if kw in query_lower),
            "analytics": sum(1 for kw in analytics_keywords if kw in query_lower),
            "inventory": sum(1 for kw in inventory_keywords if kw in query_lower),
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else "sales"

    def process(self, query: str) -> Dict[str, Any]:
        intent = self.classify_intent(query)
        agent = self.agents.get(intent)
        if not agent:
            return {"response": "No agent available for this request.", "agent": "none"}

        response = agent.process_query(query)
        return {"response": response, "agent": intent, "timestamp": str(__import__('datetime').datetime.now())}
