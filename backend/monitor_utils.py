import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Monitor, Ping, AlertLog, Plan, User

def generate_slug(name: str, user_id: int) -> str:
    raw = f"{user_id}-{name}-{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def parse_schedule(schedule: str) -> timedelta:
    """Parse a schedule string into a timedelta. Supports:
    - '*/N * * * *' cron-like shorthand (every N minutes)
    - 'every N minutes'
    - 'every N hours'
    - 'every day at HH:MM'
    """
    s = schedule.lower().strip()
    if s.startswith("*/") and "* * * *" in s:
        mins = int(s.split("*/")[1].split()[0])
        return timedelta(minutes=mins)
    if "every" in s and "minute" in s:
        parts = s.split()
        for i, p in enumerate(parts):
            if p.isdigit():
                return timedelta(minutes=int(p))
        return timedelta(minutes=5)
    if "every" in s and "hour" in s:
        parts = s.split()
        for i, p in enumerate(parts):
            if p.isdigit():
                return timedelta(hours=int(p))
        return timedelta(hours=1)
    if "every" in s and "day" in s:
        return timedelta(days=1)
    # default: 5 minutes
    return timedelta(minutes=5)

def get_next_expected(last_ping: datetime, interval: timedelta) -> datetime:
    return last_ping + interval

def check_monitor_status(monitor: Monitor) -> str:
    if monitor.last_ping_at is None:
        return "unknown"
    now = datetime.utcnow()
    interval = parse_schedule(monitor.schedule)
    expected = monitor.last_ping_at + interval + timedelta(minutes=monitor.grace_minutes)
    if now > expected + interval:  # more than 2 intervals behind
        return "down"
    if now > expected:
        return "late"
    return "ok"

def get_monitor_limits(plan: Plan) -> int:
    limits = {Plan.HOBBY: 50, Plan.PRO: 200, Plan.BUSINESS: 9999}
    return limits.get(plan, 50)

def can_create_monitor(user: User, db: Session) -> bool:
    count = db.query(Monitor).filter(Monitor.owner_id == user.id).count()
    return count < get_monitor_limits(user.plan)

def record_ping(monitor: Monitor, ip: str, user_agent: str, db: Session):
    ping = Ping(monitor_id=monitor.id, ip=ip, user_agent=user_agent)
    monitor.last_ping_at = datetime.utcnow()
    interval = parse_schedule(monitor.schedule)
    monitor.next_expected_at = get_next_expected(datetime.utcnow(), interval)
    db.add(ping)
    db.commit()
