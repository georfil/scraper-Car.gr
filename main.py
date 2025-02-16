from fastapi import FastAPI
import requests
from playwright.async_api import async_playwright
from config import querystring, base_url, url, headers
import asyncio
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/car/{page}")
def fetchCars(page: int):
    session = requests.Session()
    query = querystring.copy()  # Ensure querystring is not modified globally
    query["pg"] = page
    
    try:
        response = session.get(url=url, headers=headers, params=query)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json().get("data", {})

        if "rows" not in data:
            return {"error": "Invalid data structure in response"}
        
        # Parse car data into the desired structure
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
        return {"error": f"Request failed: {str(req_err)}"}
    
    except ValueError as val_err:
        return {"error": f"JSON decoding error: {str(val_err)}"}
    
    except Exception as ex:
        return {"error": f"An unexpected error occurred: {str(ex)}", "type": type(ex).__name__}

@app.get("/api/v2/car/{page}")
async def fetchCarsAsync(page: int):
    query = querystring.copy()  # Ensure querystring is not modified globally
    query["pg"] = page
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headless mode
        context = await browser.new_context()

        try:
            response = await context.request.get(url, headers=headers, params=query)

            if response.status == 200:
                data = await response.json()

                if "rows" not in data:
                    return {"error": "Invalid data structure in response"}
                
                # Parse car data into the desired structure
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
                
                await browser.close()
                return {"data": cars}
            else:
                await browser.close()
                return {"error": f"Request failed: {response.status} {response.status_text}"}
        
        except Exception as ex:
            await browser.close()
            return {"error": f"An unexpected error occurred: {str(ex)}", "type": type(ex).__name__}


async def fetch():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://google.com')
        x = await page.title() # Should print "Example Domain"
        await browser.close()
        await context.close()
        return x

@app.get("/api/v3")
async def run():
    return await fetch()  # Directly await the fetch function in the async route

# Fetch function to test with Playwright
