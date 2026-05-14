import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from models import Monitor, AlertLog, SessionLocal
from monitor_utils import parse_schedule, check_monitor_status
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ALERT_FROM_EMAIL

def check_all_monitors():
    if SessionLocal is None:
        return
    db = SessionLocal()
    try:
        monitors = db.query(Monitor).filter(Monitor.is_active == True).all()
        for m in monitors:
            status = check_monitor_status(m)
            if status in ("late", "down") and m.last_ping_at is not None:
                interval = parse_schedule(m.schedule)
                recent_alert = (
                    db.query(AlertLog)
                    .filter(AlertLog.monitor_id == m.id)
                    .filter(AlertLog.alert_type == "missed_ping")
                    .filter(AlertLog.sent_at > datetime.utcnow() - interval * 2)
                    .first()
                )
                if recent_alert is None:
                    alert = AlertLog(
                        monitor_id=m.id,
                        alert_type="missed_ping",
                        message=f"Monitor '{m.name}' is {status}. Last ping: {m.last_ping_at}",
                    )
                    db.add(alert)
                    db.commit()
                    if m.owner:
                        send_alert_email(m.owner.email, m.name, status)
    finally:
        db.close()

def send_alert_email(to_email: str, monitor_name: str, status: str):
    if not SMTP_HOST:
        return
    try:
        msg = MIMEText(
            f"Monitor '{monitor_name}' is {status}.\n\n"
            f"Check your dashboard: https://cronmonitor.dev/dashboard"
        )
        msg["Subject"] = f"[CronMonitor] {monitor_name} is {status.upper()}"
        msg["From"] = ALERT_FROM_EMAIL
        msg["To"] = to_email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    except Exception:
        pass
