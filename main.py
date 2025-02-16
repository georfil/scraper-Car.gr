from fastapi import FastAPI
from config import base_url, url, headers, querystring
import requests
from playwright.sync_api import sync_playwright

app = FastAPI()
# session = requests.Session()
# session.headers.update(headers)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/car/{page}")
def fetchCars(page:int):
    session = requests.Session()
    query = querystring
    querystring["pg"] = page
    try:
        response = session.get(url=url, headers=headers, params=query)
        response.raise_for_status()  # Raise an exception for HTTP errors (status codes 4xx, 5xx)
        data = response.json().get("data", {})
        if "rows" not in data:
            return {"error": "Invalid data structure in response"}
        
        cars = [{
            "id": car["id"],
            "title": car["title"],
            "make": car["title_parts"]["make"],
            "model": car["title_parts"]["model"],
            "variant": car["title_parts"]["variant"],
            "year": car["title_parts"]["year"],
            "price": car["raw_price"],
            "category": car["category"],
            "registration": car["registration"],
            "crashed": car["crashed"],
            **{
                feature["key"]: feature["value"].split(" ")[0].replace(".", "") 
                for feature in car["key_features"] 
                if feature["key"] in ("fuel_type", "gearbox_type", "special")
            },
            **{
                feature["key"]: int(feature["value"].split(" ")[0].replace(".", "")) 
                for feature in car["key_features"] 
                if feature["key"] in ("engine_size", "engine_power", "battery_range", "mileage", "charging_speed")
            },
            "is_parked": car["is_parked"]
        } for car in data["rows"]]
        
        return {"data": cars}
    
    except requests.exceptions.RequestException as req_err:
        # Catch any RequestException (e.g., connection error, timeout)
        return {"error": f"Request failed: {str(req_err)}","data":response.text}
    
    except ValueError as val_err:
        # Catch JSON decoding errors
        return {"error": f"JSON decoding error: {str(val_err)}"}
    
    except Exception as ex:
        # Catch any other type of error and return the exception type and message
        return {"error": f"An unexpected error occurred: {str(ex)}", "type": type(ex).__name__}

@app.get("/api/v2/car/{page}")
def fetchCars(page:int):
    query = querystring
    query["pg"] = page
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Run in headless mode
        context = browser.new_context()

        # Use Playwright's request API
        response = context.request.get(url, headers=headers, params=query)

        if response.status == 200:
            data = response.json()  # Convert response to JSON
            return {"data":data}  # Print formatted JSON
        else:
            print(f"Request failed: {response.status} {response.status_text}")

        browser.close()
