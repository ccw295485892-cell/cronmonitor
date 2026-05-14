# CronMonitor — Simple Cron Job Monitoring

Open-source cron job and scheduled task monitoring. Ping-based. No agents. No bloat.

## Quick Start (Self-Hosted)

```bash
git clone https://github.com/cronmonitor-dev/cronmonitor.git
cd cronmonitor/backend
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Open http://localhost:8000

## How It Works

1. Create a monitor → get a unique ping URL
2. Add a `curl` call to your crontab
3. If the ping doesn't arrive on schedule → you get an email alert

```
# Your crontab
*/5 * * * * curl -s https://your-domain.com/api/monitors/ping/abc123def456
```

## Features

- **Ping-based monitoring** — Works with any cron job, scheduled task, or background worker
- **Email alerts** — Get notified the moment a job goes silent
- **Configurable grace periods** — Don't alert on every network hiccup
- **Dashboard** — See all your monitors at a glance
- **Ping history** — 30-day history for debugging
- **Self-hosted** — Your data, your server

## Pricing

| Plan | Price | Monitors |
|---|---|---|
| Hobby | $7/mo | 50 |
| Pro | $19/mo | 200 |
| Business | $49/mo | Unlimited |

Or self-host for free.

## Tech Stack

- Python / FastAPI
- SQLite
- Tailwind CSS
- Jinja2 templates

## License

MIT
