from flask import Flask, render_template
import requests

app = Flask(__name__)

LAT_MIN = 10.0
LAT_MAX = 20.0
LON_MIN = 75.0
LON_MAX = 80.0

@app.route("/")
def index():
    api_url = (
        f"https://opensky-network.org/api/states/all?"
        f"lamin={LAT_MIN}&lomin={LON_MIN}&lamax={LAT_MAX}&lomax={LON_MAX}"
    )

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
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
                "velocity": round(state[9] * 3.6, 2) if state[9] else "N/A",  # m/s to km/h
                "heading": round(state[10], 2) if state[10] else "N/A"
            }
            flights.append(flight)

    return render_template("index.html", flights=flights)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)