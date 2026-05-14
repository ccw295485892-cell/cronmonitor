# Product Hunt Launch — CronMonitor

## Tagline
Simple cron job monitoring. Ping-based. $7/mo. Open source.

## Description
CronMonitor watches your cron jobs, scheduled tasks, and background workers so you don't have to. Add one curl line to your crontab. If your job goes silent, you get an email alert.

Why another monitoring tool? Because everything else is either bloated enterprise SaaS ($49+/mo) or unpolished open-source tools that need babysitting. CronMonitor is the middle ground: simple enough to self-host on a $5 VPS, polished enough to use as a cloud service.

Key features:
- One-line setup: curl + your unique ping URL
- Email alerts when jobs go silent
- Configurable grace periods (don't wake me up for a 30-second network hiccup)
- Dashboard with status overview and ping history
- Self-hosted (MIT) or cloud ($7/mo for 50 monitors)

Built with Python/FastAPI + SQLite. Zero dependencies on external services.

## First Comment
"Built this because I was tired of finding out my database backups had been failing for two weeks. Every dev I've talked to has this story — the cron job that ran fine for months then silently died. CronMonitor solves exactly that: one curl line, and you get an email when something stops working.

It's open source (MIT) so you can run it yourself on a $5 VPS. The cloud version is $7/mo — less than one coffee.

Happy to answer questions. Feedback welcome — this is v1 and I'm shipping improvements based on what real users need."

## Maker Info
- Solo dev
- Built in Python
- Open source (MIT)
- Launched May 2026

## Launch Checklist
- [ ] Create Product Hunt page
- [ ] Prepare screenshots/GIF (dashboard, creating monitor, alert email)
- [ ] Schedule for Tuesday-Thursday launch
- [ ] Get first 5 upvotes from beta users
- [ ] Cross-post to Hacker News (Show HN)
- [ ] Post to Reddit r/selfhosted r/devops r/Python
- [ ] Reply to every PH comment within 30 minutes
- [ ] Share on Twitter/X with screenshot
- [ ] Post to Indie Hackers
