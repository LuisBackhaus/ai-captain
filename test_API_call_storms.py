import requests

url = "https://eonet.gsfc.nasa.gov/api/v3/events?category=severeStorms"
r = requests.get(url)
data = r.json()

for event in data["events"]:
    print(event["title"])
    for geo in event["geometry"]:
        print("   Time:", geo["date"])
        print("   Coordinates:", geo["coordinates"])