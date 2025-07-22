# This webapp is broken, idk when ill fix it so bear with me :)

from flask import Flask, render_template
import requests
import os
import dotenv

app = Flask(__name__)

dotenv.load_dotenv()
CLIENT_ID = "slimeydev-api-client"
CLIENT_SECRET = os.getenv("SECRET")

LAT_MIN = 10.0
LAT_MAX = 20.0
LON_MIN = 75.0
LON_MAX = 80.0

def get_opensky_token(client_id, client_secret):
    url = "https://identity.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def get_flight_data(access_token):
    api_url = (
        f"https://opensky-network.org/api/states/all?"
        f"lamin={LAT_MIN}&lomin={LON_MIN}&lamax={LAT_MAX}&lomax={LON_MAX}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(api_url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

@app.route("/")
def index():
    try:
        access_token = get_opensky_token(CLIENT_ID, CLIENT_SECRET)
        data = get_flight_data(access_token)
    except Exception as e:
        return f"<h1>Error fetching flight data: {str(e)}</h1>"

    flights = []

    if data and "states" in data and data["states"]:
        for state in data["states"]:
            flight = {
                "icao24": state[0],
                "callsign": state[1].strip() if state[1] else "N/A",
                "origin_country": state[2],
                "time_position": state[3],
                "last_contact": state[4],
                "longitude": round(state[5], 4) if state[5] else "N/A",
                "latitude": round(state[6], 4) if state[6] else "N/A",
                "altitude": round(state[7], 2) if state[7] else "N/A",
                "velocity": round(state[9] * 3.6, 2) if state[9] else "N/A",
                "heading": round(state[10], 2) if state[10] else "N/A"
            }
            flights.append(flight)

    return render_template("index.html", flights=flights)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)