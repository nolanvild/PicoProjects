import network
import urequests
import machine
import time
import json
import requests
from secrets import SportsDataIO_API_KEY, ssid, password



def connect_to_wifi(ssid, password):
    i = 0
    print('Connecting to WiFi...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        while not wlan.isconnected() and i < 10:
            time.sleep(1)
            i += 1
            print(f"Attempt {i}: Not connected yet...")
    print('Network config:', wlan.ifconfig())
    return wlan

wlan = connect_to_wifi(ssid, password)

print(f'{wlan.isconnected()}')

# Example 2. urequests can also handle basic json support! Let's get the curren time from a server
r = urequests.get("http://example.com")
data = r
print("Success! Length:", len(r.text))

filename = "data.txt"
with open(filename, "w") as f:
    f.write(data.text)
    
def lookup_scores(teams, entries, week, year):
    print(week)
    url = f"https://api.sportsdata.io/v3/nfl/stats/json/BoxScoreByTeamFinal/{year}/{week}/{team}?key={SportsDataIO_API_KEY}"
    response = urequests.get(url)

    # Stream through the response text to find the HomeTeam
    buffer = ""
    home_team = None
    output = {}

    # Read the response in chunks to avoid memory overflow
    for entry in entries:
        chunk = response.raw.read(256)  # read 256 bytes at a time
        if not chunk:
            break
        buffer += chunk.decode()

        # Check if "HomeTeam" appears in this chunk
        if f'{entry}' in buffer:
            start = buffer.find(f'{entry}')
            # extract value following "HomeTeam":
            start_quote = buffer.find(':', start)
            end_quote = buffer.find(',', start_quote)
            data = buffer[start_quote:end_quote]
            output[f"{entry}"] = data[1:]
                
    return output
    
# Test API Call
team = "PIT"
week = 1
year = 2025
entries = ["AwayTeam", "HomeTeam", "AwayScore", "HomeScore"]
output_data = lookup_scores(team, entries, week, year)

# Print API Data
for k, v in output_data.items():
    print(f"{k}: {v}")