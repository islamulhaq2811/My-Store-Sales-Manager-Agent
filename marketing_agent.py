from sqlalchemy.orm import Session
from models import Campaign, Promotion, Lead
from datetime import datetime, timedelta
from typing import List, Dict, Any


class MarketingAgent:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, name: str, campaign_type: str = "email", budget: float = 0,
                        end_date: datetime = None, description: str = ""):
        campaign = Campaign(
            name=name,
            campaign_type=campaign_type,
            budget=budget,
            end_date=end_date,
            description=description
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_campaigns(self, status: str = None):
        query = self.db.query(Campaign)
        if status:
            query = query.filter(Campaign.status == status)
        return query.all()

    def create_promotion(self, name: str, discount_type: str, discount_value: float,
                         product_id: int = None, duration_days: int = 30):
        end_date = datetime.now() + timedelta(days=duration_days)
        promotion = Promotion(
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            product_id=product_id,
            end_date=end_date
        )
        self.db.add(promotion)
        self.db.commit()
        self.db.refresh(promotion)
        return promotion

    def get_promotions(self, status: str = "active"):
        query = self.db.query(Promotion)
        if status:
            query = query.filter(Promotion.status == status)
        return query.all()

    def add_lead(self, name: str, email: str = None, phone: str = None,
                  source: str = "website", notes: str = ""):
        lead = Lead(
            name=name,
            email=email,
            phone=phone,
            source=source,
            notes=notes
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_leads(self, status: str = None):
        query = self.db.query(Lead)
        if status:
            query = query.filter(Lead.status == status)
        return query.all()

    def get_campaign_performance(self, campaign_id: int = None):
        campaigns = self.get_campaigns() if not campaign_id else [self.db.query(Campaign).filter(Campaign.id == campaign_id).first()]
        results = []
        for camp in campaigns:
            if camp:
                results.append({
                    "id": camp.id,
                    "name": camp.name,
                    "type": camp.campaign_type,
                    "budget": camp.budget,
                    "status": camp.status,
                    "roi": round(camp.budget * 1.5, 2) if camp.budget > 0 else 0
                })
        return results

    def process_query(self, query: str) -> str:
        query_lower = query.lower()

        if "campaign" in query_lower:
            campaigns = self.get_campaigns("active")
            if campaigns:
                return f"Active campaigns: {', '.join([c.name for c in campaigns[:3]])}. Total: {len(campaigns)} campaign(s)."
            return "No active campaigns. Create one with: 'Create campaign [name]'"

        elif "promotion" in query_lower or "discount" in query_lower:
            promotions = self.get_promotions("active")
            if promotions:
                promo_list = [f"{p.name} ({p.discount_value}% off)" for p in promotions[:3]]
                return f"Active promotions: {', '.join(promo_list)}"
            return "No active promotions. Create one to boost sales!"

        elif "lead" in query_lower:
            leads = self.get_leads("new")
            return f"New leads: {len(leads)}. Total pipeline value: ${len(leads) * 1000} (estimated)"

        elif "performance" in query_lower or "roi" in query_lower:
            perf = self.get_campaign_performance()
            if perf:
                total_roi = sum(p["roi"] for p in perf)
                return f"Campaign performance: {len(perf)} campaigns, Total ROI: ${total_roi:.2f}"
            return "No campaign data available yet."

        else:
            return "Marketing Agent: I can help with campaigns, promotions, leads, and performance analysis. Try: 'Show active campaigns' or 'Create promotion 20% off'"
