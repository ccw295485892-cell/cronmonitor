import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from models import init_db
from alerting import check_all_monitors
from config import DATABASE_URL
from routes.auth_routes import router as auth_router
from routes.monitor_routes import router as monitor_router
from routes.plan_routes import router as plan_router
from routes.webhook_routes import router as webhook_router

# Initialize database at module load
init_db(DATABASE_URL)

scheduler = BackgroundScheduler()
scheduler.add_job(check_all_monitors, "interval", minutes=1, id="check_monitors")
scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

app = FastAPI(title="CronMonitor", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(monitor_router)
app.include_router(plan_router)
app.include_router(webhook_router)

# --- Frontend pages ---
@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/pricing")
def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/docs/{monitor_id}")
def monitor_detail(request: Request, monitor_id: int):
    return templates.TemplateResponse("monitor_detail.html", {"request": request, "monitor_id": monitor_id})

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
