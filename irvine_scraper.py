import json
import csv
from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG level
logger = logging.getLogger(__name__)

def clean_feature_text(text):
    """Clean up feature text by removing extra commas and spaces."""
    return text.strip().rstrip(',')

def extract_floor_from_features(features):
    """Extract floor number from features list."""
    floor_pattern = re.compile(r'(\d+)[a-z]{2} Floor|(\d+)[a-z]{2} floor')
    for feature in features:
        if 'Floor' in feature or 'floor' in feature:
            match = floor_pattern.search(feature)
            if match:
                floor_num = match.group(1) or match.group(2)
                return f"{floor_num}th Floor"
            return feature
    return "N/A"

def extract_apartment_name(plan_name):
    """Extract apartment name from floor plan name."""
    if not plan_name:
        return "Unknown"
    
    # Common apartment names in Crescent Village
    apartments = {
        'Cadiz': 'Cadiz',
        'Milano': 'Milano',
        'Mirada': 'Mirada',
        'Tesoro': 'Tesoro',
        'Toscana': 'Toscana',
        'Verona': 'Verona'
    }
    
    for apt_name in apartments:
        if apt_name in plan_name:
            return apt_name
    
    return "Unknown"

def is_two_bed_two_bath(beds_text):
    """Check if the unit is a 2 bed / 2 bath configuration."""
    logger.debug(f"Checking bed/bath configuration: {beds_text}")
    return "2 Bed / 2 Bath" in beds_text

def scrape_irvine_apartments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load configuration
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        url = config['apartments']['crescent_village']['url']
        price_range = config['apartments']['crescent_village']['filters']['price_range']
        logger.info(f"Navigating to URL: {url}")
        page.goto(url)
        
        # Wait for cookie consent if needed
        try:
            page.wait_for_selector('#onetrust-accept-btn-handler', timeout=5000)
            page.click('#onetrust-accept-btn-handler')
            logger.info("Accepted cookie consent")
        except:
            logger.info("No cookie consent needed or timed out")
        
        # Wait for page to load completely
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Additional wait for dynamic content
        
        # Check if we need to click availability
        try:
            availability_button = page.get_by_role("link", name="Availability")
            if availability_button:
                availability_button.click()
                logger.info("Clicked availability link")
                time.sleep(2)
        except:
            logger.info("Already on availability section")
        
        # Wait for floor plans to load
        page.wait_for_selector('.fapt-fp-list-item', timeout=60000)
        time.sleep(2)  # Additional wait for dynamic content
        
        # Expand all floor plans
        floor_plans = page.query_selector_all('.fapt-fp-list-item__acc-trigger-cta')
        logger.info(f"Found {len(floor_plans)} floor plans")
        
        for plan in floor_plans:
            try:
                plan.click()
                time.sleep(1)  # Give time for expansion
            except:
                logger.warning("Could not click on a floor plan")
        
        # Additional wait for all expansions to complete
        time.sleep(3)
        
        # Save the HTML content for debugging
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(page.content())
        
        # Parse the expanded content
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        # Find all unit rows
        units = []
        unit_rows = soup.select('.fapt-fp-unit__table-row:not(.fapt-fp-unit__table-row--header)')
        logger.info(f"Found {len(unit_rows)} total units")
        
        for row in unit_rows:
            try:
                # Get the floor plan name from the parent container
                plan_container = row.find_parent(class_='fapt-fp-list-item')
                if not plan_container:
                    continue
                    
                plan_name = plan_container.select_one('.fapt-fp-list-item__column--plan-name span')
                plan_name = plan_name.text.strip() if plan_name else "Unknown Plan"
                logger.debug(f"Processing plan: {plan_name}")
                
                # Extract unit details
                unit_name = row.select_one('.fapt-fp-unit__unit-name-text')
                beds = plan_container.select_one('.fapt-fp-list-item__column--beds-baths')  # Updated selector
                term = row.select_one('.fapt-fp-unit__column-inner--term span')
                price = row.select_one('.fapt-fp-unit__column-inner--price span')
                available = row.select_one('.fapt-fp-unit__column-inner--available span')
                features = row.select_one('.fapt-fp-unit__column-inner--amenities div')
                
                if not all([unit_name, beds, term, price, available, features]):
                    logger.debug("Missing required fields")
                    continue
                
                # Check if it's a 2 bed / 2 bath unit
                beds_text = beds.get_text(strip=True)
                logger.debug(f"Found configuration: {beds_text}")
                if not is_two_bed_two_bath(beds_text):
                    logger.debug(f"Skipping non-2bed/2bath unit: {beds_text}")
                    continue
                
                # Clean up the text
                price_text = price.text.strip().replace('$', '').replace(',', '')
                price_value = float(price_text)
                
                # Extract features and clean them up
                feature_texts = []
                for feat in features.select('span'):
                    text = clean_feature_text(feat.text)
                    if text:
                        feature_texts.append(text)
                
                # Extract floor from features
                floor = extract_floor_from_features(feature_texts)
                
                # Check if price is within range
                if price_range[0] <= price_value <= price_range[1]:
                    unit_info = {
                        'Apartment': extract_apartment_name(plan_name),
                        'BLDG NO. / APT NO.': unit_name.text.strip(),
                        'TERM': term.text.strip(),
                        'PRICE': f"${price_text}",
                        'AVAILABLE': available.text.strip(),
                        'Floor': floor,
                        'FEATURES': ', '.join(feature_texts)
                    }
                    units.append(unit_info)
                    logger.info(f"Found matching 2 bed/2 bath unit: {unit_info['BLDG NO. / APT NO.']} at {unit_info['PRICE']} in {unit_info['Apartment']}")
            except Exception as e:
                logger.error(f"Error processing unit: {str(e)}")
        
        # Save results to CSV
        if units:
            fieldnames = ['Apartment', 'BLDG NO. / APT NO.', 'TERM', 'PRICE', 'AVAILABLE', 'Floor', 'FEATURES']
            with open('apartments.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(units)
            logger.info(f"Saved {len(units)} 2 bed/2 bath units to apartments.csv")
        else:
            logger.warning("No matching 2 bed/2 bath apartments found")
        
        # Save final state screenshot
        page.screenshot(path='final_state.png')
        browser.close()

if __name__ == "__main__":
    scrape_irvine_apartments() 