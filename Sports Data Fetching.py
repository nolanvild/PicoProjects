import network
import urequests
import machine
import ntptime
import time
import json
import requests
import os
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

# Set the time for game checks
def get_eastern_time():
    ntptime.host = 'pool.ntp.org'
    ntptime.settime()
    rtc = machine.RTC()
    current_time = rtc.datetime()
    eastern_time = list(current_time)
    eastern_time[4] = (eastern_time[4] - 4 )%24
    return eastern_time
eastern_time = get_eastern_time()
print(f"The current time is: {eastern_time}")


    
def lookup_scores(teams, entries, week, year):
    # Box score - by Team [Final]
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
            print("No chunk to read")
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
    response.close()
    return output
    
# Test API Call
team = "PIT"
weeks = [1, 2, 3, 4, 5, 6, 7]
year = 2025
entries = ["AwayTeam", "HomeTeam", "AwayScore", "HomeScore"]
json_filename = f"{team}_year{year}.json"

for week in weeks:
    output_data = lookup_scores(team, entries, week, year)

    try:
        os.stat(json_filename)
        file_exists = True
    except OSError:
        file_exists = False
    
    if not file_exists:
        file_data = {}
    else:
        with open(json_filename, 'r') as f:
            file_data = json.load(f)
            file_data[f"{week}"] = output_data
        
    with open(json_filename, 'w') as f:
        json.dump(file_data, f)
            
with open(json_filename, 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        print(f"{k}: {v}")
    