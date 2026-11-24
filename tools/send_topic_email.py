#!/usr/bin/env python3
"""Email today's topic list.
Uses content/topic-lists/<today>.email.html (written by the scheduled Claude topic-list task).
If that task didn't run, sends the scanner's top picks from the newest digest instead.
SMTP settings come from environment variables (GitHub secrets):
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO, MAIL_FROM (optional), TOPIC_PAGE_URL (optional)."""
import os, re, sys, html, smtplib, glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_config as EC

today = EC.today().isoformat()
root = EC.ROOT
site = EC.SITE_NAME
page_url = os.environ.get("TOPIC_PAGE_URL") or ""

full = os.path.join(root, "content", "topic-lists", f"{today}.email.html")
if os.path.exists(full):
    body = open(full).read()
    subject = f"{site} topics — {today}"
else:
    digests = sorted(glob.glob(os.path.join(root, "scanner", "sources", "digests", "digest-*.md")))
    if not digests:
        sys.exit("No topic list and no digest found; nothing to send.")
    md = open(digests[-1]).read()
    picks = re.findall(r"^- \[(.+?)\]\((\S+?)\) — (.+?)(?:  ·|  `|$)", md.split("## Other")[0], re.M)[:25]
    rows = "".join(f'<li><a href="{html.escape(u)}">{html.escape(t)}</a> — {html.escape(s)}</li>' for t, u, s in picks)
    body = (f'<div style="font-family:Arial,sans-serif;max-width:680px"><h2>{html.escape(site)} — scanner top picks</h2>'
            f'<p>The full topic list wasn\'t built today, so here are the scanner\'s top picks from {os.path.basename(digests[-1])[7:17]}.</p>'
            f'<ol>{rows}</ol>' + (f'<p><a href="{page_url}">Last full topic list</a></p>' if page_url else '') + '</div>')
    subject = f"{site} top picks — {today} (topic list not built)"

to = os.environ.get("MAIL_TO")
if not to:
    sys.exit("Set the MAIL_TO repository variable (Settings → Secrets and variables → Actions → Variables); email not sent.")
host, user, pw = os.environ.get("SMTP_HOST"), os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
if not (host and user and pw):
    sys.exit("SMTP_HOST, SMTP_USER and SMTP_PASS secrets are not set yet; email not sent.")
port = int(os.environ.get("SMTP_PORT") or 587)
msg = MIMEMultipart("alternative")
msg["Subject"], msg["From"], msg["To"] = subject, os.environ.get("MAIL_FROM") or user, to
msg.attach(MIMEText("Open in a mail app that shows HTML." + (f" Or view the page: {page_url}" if page_url else ""), "plain"))
msg.attach(MIMEText(body, "html"))
with (smtplib.SMTP_SSL(host, port) if port == 465 else smtplib.SMTP(host, port)) as s:
    if port != 465:
        s.starttls()
    s.login(user, pw)
    s.sendmail(msg["From"], [a.strip() for a in to.split(",")], msg.as_string())
print("sent", subject, "to", to)
