import os
import datetime as dt
from pathlib import Path
import pandas as pd
import smtplib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Resolve workspace: prefer GITHUB_WORKSPACE on runners, else use repo-relative path
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parent))

# Paths
CSV_PATH = WORKSPACE / "birthdays.csv"
TEMPLATE_PATH = WORKSPACE / "letter_templates" / "letter_1.txt"

logging.info(f"Using workspace: {WORKSPACE}")
logging.info(f"Looking for CSV at: {CSV_PATH}")
logging.info(f"Looking for template at: {TEMPLATE_PATH}")

# Basic checks
if not CSV_PATH.exists():
    logging.error(f"birthdays.csv not found at {CSV_PATH}")
    raise SystemExit(1)

if not TEMPLATE_PATH.exists():
    logging.error(f"Template not found at {TEMPLATE_PATH}")
    raise SystemExit(1)

# Read data
df = pd.read_csv(CSV_PATH)

now = dt.datetime.now()
month_now = int(now.month)
day_now = int(now.day)

# Normalize columns (handles strings in CSV)
if "month" in df.columns:
    df["month"] = df["month"].astype(int)
if "day" in df.columns:
    df["day"] = df["day"].astype(int)

# Find birthdays for today
matches = df[(df["month"] == month_now) & (df["day"] == day_now)]
if matches.empty:
    logging.info("No birthdays for today. Exiting.")
    raise SystemExit(0)

# Read template once
template_text = TEMPLATE_PATH.read_text()

# Email credentials
SENDER = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("MY_PASSWORD")
if not SENDER or not PASSWORD:
    logging.error("Environment variables MY_EMAIL and/or MY_PASSWORD are not set.")
    raise SystemExit(1)

# Send emails for each match
for _, row in matches.iterrows():
    try:
        name = row.get("name") or "Friend"
        recipient = row.get("email") or SENDER

        body = template_text.replace("[NAME]", str(name))
        subject = "Happy Birthday!"
        message = f"Subject: {subject}\n\n{body}"

        logging.info(f"Sending birthday email to {recipient} (for {name})")
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=SENDER, password=PASSWORD)
            connection.sendmail(from_addr=SENDER, to_addrs=recipient, msg=message)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.exception(f"Failed to send email to {recipient}: {e}")
