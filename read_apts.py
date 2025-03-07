import json
import requests
import csv
from bs4 import BeautifulSoup

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)

def fetch_apartments(apartment):
    url = config["apartments"][apartment]["url"]
    headers = {"User-Agent": config["scraper"]["user_agent"]}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data for {apartment}. Status Code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    selectors = config["apartments"][apartment]["selectors"]
    
    apartments_list = []
    
    for unit in soup.select(selectors["unit"]):
        try:
            beds = unit.select_one(selectors["beds"]).text.strip()
            price = unit.select_one(selectors["price"]).text.strip()
            floor = unit.select_one(selectors.get("floor", "")).text.strip() if selectors.get("floor") else "N/A"
            availability = unit.select_one(selectors.get("availability", "")).text.strip() if selectors.get("availability") else "N/A"
            
            apartments_list.append({
                "Apartment": apartment,
                "Beds": beds,
                "Price": price,
                "Floor": floor,
                "Availability": availability
            })
        except AttributeError:
            continue
    
    return apartments_list

def save_to_csv(apartments):
    with open("apartments.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Apartment", "Beds", "Price", "Floor", "Availability"])
        writer.writeheader()
        writer.writerows(apartments)
    print("Data saved to apartments.csv")

if __name__ == "__main__":
    all_apartments = []
    for apt in config["apartments"].keys():
        all_apartments.extend(fetch_apartments(apt))
    
    save_to_csv(all_apartments)
