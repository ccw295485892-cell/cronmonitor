from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, Plan, get_db
from schemas import PlanUpgrade, UserOut
from auth import require_user

router = APIRouter(prefix="/api/plans", tags=["plans"])

PLANS = {
    "hobby": {"name": "Hobby", "price": "$7/mo", "monitors": 50, "features": ["50 monitors", "Email alerts", "5-min check intervals"]},
    "pro": {"name": "Pro", "price": "$19/mo", "monitors": 200, "features": ["200 monitors", "Email alerts", "1-min check intervals", "Team access (3 seats)", "Webhook notifications"]},
    "business": {"name": "Business", "price": "$49/mo", "monitors": "∞", "features": ["Unlimited monitors", "Priority alerts", "30-second intervals", "Unlimited team seats", "Webhooks", "White-label status page", "API access"]},
}

@router.get("")
def list_plans():
    return PLANS

@router.get("/current", response_model=dict)
def current_plan(user: User = Depends(require_user)):
    return {"plan": user.plan.value, "details": PLANS[user.plan.value]}

@router.post("/upgrade", response_model=dict)
def upgrade_plan(data: PlanUpgrade, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if data.plan not in [p.value for p in Plan]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    user.plan = Plan(data.plan)
    db.commit()
    return {"plan": user.plan.value, "details": PLANS[user.plan.value]}
