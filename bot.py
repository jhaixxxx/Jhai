import requests
import time
import json
import sys

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

# Create session
session = requests.Session()

def send_request(name, url, data=None, method="POST"):
    """Helper function to send a request and format the response."""
    print(f"\n[🔄] Sending {method} request to {name}...")

    # Send request
    if method == "POST":
        response = session.post(url, headers=headers, json=data)
    else:
        response = session.get(url, headers=headers)

    # Format response
    try:
        response_json = response.json()  # Parse JSON response
        formatted_response = json.dumps(response_json, indent=4)
    except json.JSONDecodeError:
        formatted_response = response.text  # Raw text if not JSON

    print(f"[✔] {name} - Status: {response.status_code}")
    print(f"[📩] Response:\n{formatted_response}")
    return response

def countdown(seconds, message):
    """Countdown timer with live updating display."""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r[⏳] {message} in {remaining}s...  ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r[✅] Resuming...\n")

# Counter initialization
counter = 1

while True:
    print(f"\n======== [ 🔄 Cycle {counter} ] ========")

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



    # Step 3: End Session
    send_request("End Session", f"{base_url}/endActiveSession", method="GET")

    # Increment counter
    counter += 1
