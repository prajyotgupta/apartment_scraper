import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)
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
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')  # Disable notifications
    chrome_options.add_argument('--disable-extensions')    # Disable extensions
    
    # Initialize the Chrome WebDriver
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Load configuration
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        url = config['apartments']['crescent_village']['url']
        price_range = config['apartments']['crescent_village']['filters']['price_range']
        logger.info(f"Navigating to URL: {url}")
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for cookie consent if needed
        try:
            cookie_button = wait.until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            cookie_button.click()
            logger.info("Accepted cookie consent")
        except:
            logger.info("No cookie consent needed or timed out")
        
        # Check if we need to click availability
        try:
            availability_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Availability")))
            availability_button.click()
            logger.info("Clicked availability link")
            time.sleep(2)
        except:
            logger.info("Already on availability section")
        
        # Wait for floor plans to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'fapt-fp-list-item')))
        time.sleep(2)
        
        # Expand all floor plans
        floor_plans = driver.find_elements(By.CLASS_NAME, 'fapt-fp-list-item__acc-trigger-cta')
        logger.info(f"Found {len(floor_plans)} floor plans")
        
        for plan in floor_plans:
            try:
                driver.execute_script("arguments[0].click();", plan)
                time.sleep(1)
            except:
                logger.warning("Could not click on a floor plan")
        
        # Additional wait for all expansions to complete
        time.sleep(3)
        
        # Parse the expanded content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
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
                beds = plan_container.select_one('.fapt-fp-list-item__column--beds-baths')
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
        
        # Save screenshot
        driver.save_screenshot('final_state.png')
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_irvine_apartments() 