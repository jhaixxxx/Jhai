from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/getActiveSession", methods=["POST"])
def get_active_session():
    url = "https://boats-app-cba6ae7713ab.herokuapp.com/getActiveSession"
    
    headers = {
        "currency": "USD",
        "Connection": "close",
        "rentappsetup": "true",
        "version": "2.7",
        "language": "English",
        "packageName": "com.boat.app.adventure",
        "versionCode": "27",
        "storeType": "google_play",
        "authcode": "ofimgk8:g9>",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/5.0.0-alpha.14"
    }
    
    payload = request.json
    response = requests.post(url, headers=headers, json=payload)

    return jsonify({
        "status_code": response.status_code,
        "response_body": response.json()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
