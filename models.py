from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os, requests
from urllib.parse import quote

DB_URL=os.environ.get('DB_URL')

APPS_SCRIPT_URL = os.environ.get('APPS_SCRIPT_URL')

conn = None
Variables = None
HostedUrls = None
Logs = None
conn_message = None
if not conn:
    conn_message ="No existing connection, connecting"
    conn = MongoClient(DB_URL)

    db = conn.get_database("main_db")
    HostedUrls = db.get_collection("hosted_urls")
    Variables = db.get_collection("variables")
    Logs = db.get_collection("logs")
else:
    conn_message = "Connectin exists"
