import requests

BASE = "http://127.0.0.1:5000/"


# response = requests.post(BASE + "addCar", {"brand": "toyota", "model": "hilux", "year": 2018, "color": "black"})

# response = requests.post(BASE + "addEntry", {"car_id": 1, "value": 430000, "mileage": 110500, "date": "08-07-2021"})

response = requests.get(BASE + "getCars")


print(response.json())