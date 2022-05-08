# Import the required library
from geopy.geocoders import Nominatim
import requests
import json
import unidecode

def get_destinations():
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")
    API_key = 'My_API_Key'
    destinations = []
    #just mocking the data
    location = geolocator.geocode('Washington')
    lon = location.longitude
    lat = location.latitude
    url = f"https://api.opentripmap.com/0.1/en/places/bbox?lon_min={lon-0.1}&lon_max={lon+0.1}&lat_min={lat-0.1}&lat_max={lat+0.1}&kinds=historic&rate=3h&format=json&apikey={API_key}"
    response = requests.get(url)
    #f = open("r1.txt", "r")
    response_json = json.loads(response.text)
    
    for index, destination in enumerate(response_json):
        name = f"{response_json[index]['name']}"
        unidecode.unidecode(name)
        destinations.append(name.replace(" ", "+"))
    return destinations[:16]




