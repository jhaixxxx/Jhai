import requests
import time
import json
import threading
from flask import Flask, jsonify

app = Flask(__name__)

# Base URL
base_url = "https://boats-app-cba6ae7713ab.herokuapp.com"

# Common headers
headers = {
    "currency": "USD",
    "Connection": "close",
    "rentappsetup": "true",
    "version": "2.7",
    "language": "English",
    "packageName": "com.boat.app.adventure",
    "versionCode": "27",
    "storeType": "google_play",
    "authcode": "g5relk8:g9>",
    "Content-Type": "application/json; charset=utf-8",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/5.0.0-alpha.14"
}

# Logs storage
logs = []
running = False

def send_request(name, url, data=None, method="POST"):
    """Send a request and format response."""
    log(f"🔄 Sending {method} request to {name}...")

    # Send request
    if method == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)

    # Format response
    try:
        response_json = response.json()  # Parse JSON response
        formatted_response = json.dumps(response_json, indent=4)
    except json.JSONDecodeError:
        formatted_response = response.text  # Raw text if not JSON

    log(f"✔ {name} - Status: {response.status_code}")
    log(f"📩 Response:\n{formatted_response}")

def countdown(seconds, message):
    """Countdown timer with logging."""
    for remaining in range(seconds, 0, -1):
        log(f"⏳ {message} in {remaining}s...")
        time.sleep(1)

def log(message):
    """Store logs and limit to last 50 messages."""
    logs.append(message)
    if len(logs) > 50:
        logs.pop(0)
    print(message)  # For Render logs

def process_loop():
    """Main processing loop that runs indefinitely."""
    global running
    counter = 1
    while running:
        log(f"\n======== [ 🔄 Cycle {counter} ] ========")

        # Step 1: Create New Session
        create_session_data = {
            "verificationCode": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b71ce94faf1edc631739ef5ccac5af7fc"
        }
        send_request("Create New Session", f"{base_url}/createNewSession", create_session_data)

        # Wait 60 seconds
        countdown(60, "Waiting after Create Session")

        # Step 2: Get Cycle Ads Reward
        reward_data = {
            "verificationCode": "5a52eb89e0208ead2c23809a536a876a5c06d3e446d4fa13466afac52b1fd026cba3b08ad5796791021c91b120cedc2b85b8018ca51c680a99bbd26680f4217c"
        }
        send_request("Get Cycle Ads Reward", f"{base_url}/getCycleAdsReward", reward_data)

        # Wait 30 seconds
        countdown(30, "Waiting after Get Cycle Ads Reward")

        # Step 3: End Session
        send_request("End Session", f"{base_url}/endActiveSession", method="GET")

        counter += 1

@app.route("/start", methods=["GET"])
def start():
    """Start the process loop."""
    global running
    if not running:
        running = True
        thread = threading.Thread(target=process_loop)
        thread.start()
        return jsonify({"status": "Started processing loop"}), 200
    return jsonify({"status": "Already running"}), 400

@app.route("/stop", methods=["GET"])
def stop():
    """Stop the process loop."""
    global running
    running = False
    return jsonify({"status": "Stopped processing loop"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    """Fetch the last 50 logs."""
    return jsonify({"logs": logs}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
