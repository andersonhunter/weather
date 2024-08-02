import time
import zmq
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import urllib.request
import json


def get_coordinates(data: list) -> list:
    """
    Get the coordinates from Geocoding API.
    Return data array [startdate, enddate, lat, long, params]
    """
    location = data[2] + "+US"
    with urllib.request.urlopen(
            f"https://geocode.maps.co/search?q={location}&api_key=66a67b95bc4b5457128211neq06f8d9") as url:
        coords = json.load(url)
        lat, long = coords[0]['lat'], coords[0]['lon']
    data[2] = lat
    data.insert(3, long)
    return data


def get_climate_data(data: list) -> list:
    """
    Receive a list with [startdate, enddate, lat, long, params]
    Return the user-selected climate data as an array
    """
    # Setup Open-Meteo API client w/ cache and retry on error
    cache_sessions = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_sessions, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": arr[2],
        "longitude": arr[3],
        "start_date": arr[1],
        "end_date": arr[0],
        "daily": arr[4],
        "temperature_unit": "fahrenheit",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location, use for loop for more by incrementing responses index
    response = responses[0]
    print(f"Coordinates {response.Latitude()}, {response.Longitude()}")
    daily = response.Daily()
    results = daily.Variables(0).ValuesAsNumpy()
    print(f"Results: {results}")
    output = []
    # Convert the numpy array into a python array. Round each number to
    for item in results:
        output.append(int(round(item.item(), 2) * 100))
    return output


while True:
    # Set up the server to receive data from app.py
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    message = socket.recv()
    print(f"Received request from app.py: {message.decode()}")
    if len(message) > 0:
        response_body = message.decode()
        # Split search criteria into array elements in order: startdate, enddate, location, params
        arr = [item for item in response_body.split(", ")]
        # Get the coordinates for the chosen location
        data = get_coordinates(arr)
        # Get the climate data with input [start, end, lat, long, params]
        return_message = get_climate_data(arr)

        # Convert return message to a comma delimited string instead of array
        return_string = ""
        for x in range(len(return_message) - 1):
            return_string += (str(return_message[x]) + ", ")
        return_string += str(return_message[len(return_message) - 1])
        print(f'Sending data to client: {return_string}')
        socket.send_string(return_string)

