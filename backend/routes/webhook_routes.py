# Lemon Squeezy payment webhook handler
import hashlib
import hmac
import json
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from models import User, Plan, get_db
from config import LEMONSQUEEZY_WEBHOOK_SECRET

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("x-signature", "")

    if LEMONSQUEEZY_WEBHOOK_SECRET:
        expected = hmac.new(
            LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(raw_body)
    event_name = payload.get("meta", {}).get("event_name", "")
    data = payload.get("data", {})
    attributes = data.get("attributes", {})

    # Handle order completed
    if event_name == "order_created":
        customer_email = attributes.get("user_email", "").strip().lower()
        variant_name = attributes.get("variant_name", "").lower()

        user = db.query(User).filter(User.email == customer_email).first()
        if user is None:
            # Auto-create user for checkout
            from auth import hash_password
            import secrets
            user = User(
                email=customer_email,
                hashed_password=hash_password(secrets.token_urlsafe(16))
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        plan_map = {"hobby": Plan.HOBBY, "pro": Plan.PRO, "business": Plan.BUSINESS}
        if variant_name in plan_map:
            user.plan = plan_map[variant_name]
            db.commit()

    elif event_name == "subscription_cancelled":
        customer_email = attributes.get("user_email", "").strip().lower()
        user = db.query(User).filter(User.email == customer_email).first()
        if user:
            user.plan = Plan.HOBBY
            db.commit()

    return {"ok": True}
