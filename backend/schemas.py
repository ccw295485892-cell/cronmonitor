from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    plan: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MonitorCreate(BaseModel):
    name: str
    schedule: str  # e.g. "*/5 * * * *" or "every 30 minutes"
    grace_minutes: int = 5

class MonitorOut(BaseModel):
    id: int
    name: str
    slug: str
    schedule: str
    grace_minutes: int
    is_active: bool
    created_at: datetime
    last_ping_at: Optional[datetime] = None
    next_expected_at: Optional[datetime] = None
    status: str = "unknown"  # "ok", "late", "down"

class PingOut(BaseModel):
    id: int
    monitor_id: int
    timestamp: datetime
    ip: Optional[str] = None

class AlertOut(BaseModel):
    id: int
    monitor_id: int
    alert_type: str
    sent_at: datetime
    message: Optional[str] = None

class DashboardStats(BaseModel):
    total_monitors: int
    monitors_ok: int
    monitors_late: int
    monitors_down: int
    total_pings_today: int

class PlanUpgrade(BaseModel):
    plan: str  # "hobby", "pro", "business"
    lemon_squeezy_order_id: Optional[str] = None
