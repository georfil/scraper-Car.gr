from fastapi import FastAPI
from config import base_url, url, headers, querystring
import requests

app = FastAPI()
session = requests.Session()
session.headers.update(headers)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/car/{page}")
def fetchCars(page:int):
    query = querystring
    querystring["pg"] = page
    try:
        response = session.get(url=url, params=query)
        data = response.json()["data"]["results"]
        cars = [{
                "id":car["id"],
                "title":car["title"],
                "make":car["title_parts"]["make"],
                "model":car["title_parts"]["model"],
                "variant":car["title_parts"]["variant"],
                "year":car["title_parts"]["year"],
                "price":car["raw_price"],
                "category":car["category"],
                "registration":car["registration"],
                "crashed":car["crashed"],
                **{
                    feature["key"]:feature["value"].split(" ")[0].replace(".","") for feature in car["key_features"] if feature["key"] in ("fuel_type","gearbox_type","special")
                },
                **{
                    feature["key"]:int(feature["value"].split(" ")[0].replace(".","")) for feature in car["key_features"] if feature["key"] in ("engine_size","engine_power","battery_range","mileage","charging_speed")
                },
                "is_parked":car["is_parked"]} for car in data["rows"]]
        return {"data":cars}
    except:
        return {"error"}



