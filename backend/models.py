import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

class Base(DeclarativeBase):
    pass

class Plan(str, enum.Enum):
    HOBBY = "hobby"
    PRO = "pro"
    BUSINESS = "business"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    plan = Column(Enum(Plan), default=Plan.HOBBY)
    monitors = relationship("Monitor", back_populates="owner")
    created_at = Column(DateTime, default=datetime.utcnow)

class Monitor(Base):
    __tablename__ = "monitors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    schedule = Column(String, nullable=False)
    grace_minutes = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="monitors")
    pings = relationship("Ping", back_populates="monitor")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_ping_at = Column(DateTime, nullable=True)
    next_expected_at = Column(DateTime, nullable=True)

class Ping(Base):
    __tablename__ = "pings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"))
    monitor = relationship("Monitor", back_populates="pings")
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

class AlertLog(Base):
    __tablename__ = "alert_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"))
    monitor = relationship("Monitor")
    alert_type = Column(String, default="missed_ping")
    sent_at = Column(DateTime, default=datetime.utcnow)
    message = Column(Text, nullable=True)

SessionLocal = None

def init_db(database_url="sqlite:///./cronmonitor.db"):
    global SessionLocal
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
