import os
import logging
from urllib.parse import urlparse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import psycopg2
import requests
import re
import pytz
from datetime import datetime
logging.basicConfig(level=logging.DEBUG)

# Initializes your app with your bot token and socket mode handler
app = App(name='FindMySteve', token=os.environ.get("SLACK_BOT_TOKEN"))
handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
pg_uri = os.environ.get("DATABASE_URL")
google_api_key = os.environ.get("GOOGLE_API_KEY")
result = urlparse(pg_uri)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

# Function to get the latest location of Steve
def get_steve_location():
    db_conn = psycopg2.connect(
        dbname = database,
        user = username,
        password = password,
        host = hostname,
        port = port
    ) 
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT lat, lon FROM locations WHERE username = 'steve' ORDER BY created_at DESC LIMIT 1")
        lat, lon = cursor.fetchone()
        return lat, lon

# Function to get city from latitude and longitude using Google Geocoding API
def get_city(lat, lon):
    api_key = google_api_key  # Replace with your Google API key
    response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}")
    data = response.json()

    if data['results']:
        for component in data['results'][0]['address_components']:
            if 'locality' in component['types']:
                locality = f"{component['long_name']}, "
            else:
                locality = ""
            if 'administrative_area_level_1' in component['types']:
                # Fallback to administrative area level 1 if locality is not available
                city = f"{component['long_name']}, "
            else:
                city = ""
            if 'country' in component['types']:
                country = component['long_name']
        location = f"{locality}{city}{country}"
        if location == "":
            return "Location not found"
        else:
            return location
    else:
        return "Location not found"
    
def post_message(lat, lon):
    location = get_city(lat, lon)

    image_url = get_map_image(location)
    time = get_steve_time(lat, lon)
    if image_url:
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Steve was last seen in *{location}*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"It's currently *{time}* for Steve"
                    }
                },
                {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "Image"
                }
            ],
            "unfurl_links": False
        }
        return message
    else:
        return "No image found for the specified location."

def get_map_image(city_name, map_size="400x200", zoom=12):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={google_api_key}"
    response = requests.get(geocode_url)
    if response.status_code != 200:
        return "Error: Could not retrieve location data"

    geocode_data = response.json()
    if not geocode_data['results']:
        return "Error: Location not found"

    location = geocode_data['results'][0]['geometry']['location']
    lat, lon = location['lat'], location['lng']

    # Now, use the Static Maps API to get the map image URL
    static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&size={map_size}&key={google_api_key}&markers=color:red|label:C|{lat},{lon}"
    return static_map_url

def get_steve_time(lat, lon):
    timezone_url = f"https://maps.googleapis.com/maps/api/timezone/json?location={lat},{lon}&timestamp={int(datetime.utcnow().timestamp())}&key={google_api_key}"
    timezone_response = requests.get(timezone_url)
    timezone_data = timezone_response.json()
    print(timezone_data)
    if timezone_data['status'] != "OK":
        return "Timezone information not found."

    # Calculate local time
    timezone_id = timezone_data['timeZoneId']
    timezone = pytz.timezone(timezone_id)
    local_time = datetime.now(timezone)
    return local_time.strftime("%-I:%M%p, %A, %b %-d (%Z; %z)")

# Listens to incoming messages that contain "where is steve?"
@app.message(re.compile("where is steve.?", re.I))
def message_hello(say, context):
    lat, lon = get_steve_location()
    say(post_message(lat, lon))

@app.message(re.compile("when is steve.?", re.I))
def message_when(say, context):
    lat, lon = get_steve_location()
    say(f"It is currently {get_steve_time(lat, lon)} for Steve")

@app.event("message")
def handle_message_events(body, logger):
    return

if __name__ == "__main__":
    handler.start()
