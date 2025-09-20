
import requests
import json
from dotenv import load_dotenv
import os
from urllib.parse import quote


# --- Load Environment ---
load_dotenv()
DEFAULT_BOT_TOKEN = os.environ.get('BOT_TOKEN')
HOSTED_URL = os.environ.get('HOSTED_URL')
USER_ID = os.environ.get("USER_ID")

def _send_telegram_message(text, reply_markup=None):
    base_url = f"https://api.telegram.org/bot{DEFAULT_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': str(USER_ID), 'text': text}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(base_url, data=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        return False