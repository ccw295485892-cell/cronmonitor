import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import User, Monitor, Ping, AlertLog, get_db
from schemas import MonitorCreate, MonitorOut, PingOut, AlertOut, DashboardStats
from auth import require_user, get_current_user
from monitor_utils import generate_slug, record_ping, check_monitor_status, can_create_monitor, get_monitor_limits
from datetime import datetime

router = APIRouter(prefix="/api/monitors", tags=["monitors"])

@router.get("", response_model=list[MonitorOut])
def list_monitors(user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitors = db.query(Monitor).filter(Monitor.owner_id == user.id).all()
    return [format_monitor(m) for m in monitors]

@router.post("", response_model=MonitorOut)
def create_monitor(data: MonitorCreate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not can_create_monitor(user, db):
        limit = get_monitor_limits(user.plan)
        raise HTTPException(status_code=403, detail=f"Monitor limit reached ({limit}). Upgrade your plan.")
    slug = generate_slug(data.name, user.id)
    monitor = Monitor(
        name=data.name, slug=slug, schedule=data.schedule,
        grace_minutes=data.grace_minutes, owner_id=user.id
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return format_monitor(monitor)

@router.get("/{monitor_id}", response_model=MonitorOut)
def get_monitor(monitor_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id, Monitor.owner_id == user.id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return format_monitor(monitor)

@router.delete("/{monitor_id}")
def delete_monitor(monitor_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id, Monitor.owner_id == user.id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    db.query(Ping).filter(Ping.monitor_id == monitor.id).delete()
    db.query(AlertLog).filter(AlertLog.monitor_id == monitor.id).delete()
    db.delete(monitor)
    db.commit()
    return {"ok": True}

@router.get("/{monitor_id}/pings", response_model=list[PingOut])
def get_pings(monitor_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id, Monitor.owner_id == user.id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    pings = db.query(Ping).filter(Ping.monitor_id == monitor.id).order_by(Ping.timestamp.desc()).limit(50).all()
    return pings

@router.get("/{monitor_id}/alerts", response_model=list[AlertOut])
def get_alerts(monitor_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id, Monitor.owner_id == user.id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    alerts = db.query(AlertLog).filter(AlertLog.monitor_id == monitor.id).order_by(AlertLog.sent_at.desc()).limit(20).all()
    return alerts

@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(user: User = Depends(require_user), db: Session = Depends(get_db)):
    monitors = db.query(Monitor).filter(Monitor.owner_id == user.id).all()
    ok = late = down = 0
    for m in monitors:
        s = check_monitor_status(m)
        if s == "ok": ok += 1
        elif s == "late": late += 1
        elif s == "down": down += 1
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pings_today = db.query(Ping).join(Monitor).filter(
        Monitor.owner_id == user.id, Ping.timestamp >= today
    ).count()
    return DashboardStats(
        total_monitors=len(monitors), monitors_ok=ok,
        monitors_late=late, monitors_down=down, total_pings_today=pings_today
    )

# Public ping endpoint — no auth needed, called by cron jobs
@router.post("/ping/{slug}")
@router.get("/ping/{slug}")
def public_ping(slug: str, request: Request, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.slug == slug, Monitor.is_active == True).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")
    record_ping(monitor, ip, ua, db)
    return {"ok": True, "monitor": monitor.name}

def format_monitor(m: Monitor) -> MonitorOut:
    return MonitorOut(
        id=m.id, name=m.name, slug=m.slug, schedule=m.schedule,
        grace_minutes=m.grace_minutes, is_active=m.is_active,
        created_at=m.created_at, last_ping_at=m.last_ping_at,
        next_expected_at=m.next_expected_at, status=check_monitor_status(m)
    )
