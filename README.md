# Crescent Village Apartment Scraper

A Python script that automatically scrapes and monitors apartment availability at Crescent Village in San Jose. The script specifically tracks 2 bed/2 bath units across different apartment buildings within the complex.

## Features

- **Targeted Search**: Focuses on 2 bed/2 bath units only
- **Multi-building Coverage**: Tracks units across all Crescent Village buildings:
  - Cadiz
  - Milano
  - Mirada
  - Tesoro
  - Toscana
  - Verona
- **Comprehensive Data**: Extracts detailed information for each unit:
  - Building and apartment number
  - Lease term
  - Monthly rent
  - Availability date
  - Floor number
  - Detailed features and amenities
- **Price Filtering**: Configurable price range filter (default: $3,000 - $4,200)
- **Automated Process**: Handles website navigation and data extraction automatically

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/apartment_scraper.git
cd apartment_scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

## Configuration

The script uses `config/config.json` for configuration. Here's how to customize the settings:

1. Open `config/config.json` in your text editor
2. Modify the configuration options:

```json
{
  "apartments": {
    "crescent_village": {
      "url": "https://www.irvinecompanyapartments.com/locations/northern-california/san-jose/crescent-village/availability.html",
      "filters": {
        "beds": "2 Bed / 2 Bath",
        "price_range": [3000, 4200]
      }
    }
  },
  "scraper": {
    "interval_minutes": 30,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  }
}
```

### Configuration Options:

#### Apartment Settings
- `url`: The URL of the apartment listing page
- `filters`:
  - `price_range`: Array of [min_price, max_price] in dollars
    - Example: `[3000, 4200]` will only show units between $3,000 and $4,200
  - `beds`: The bed/bath configuration to filter for (default: "2 Bed / 2 Bath")

#### Scraper Settings
- `interval_minutes`: How often to check for updates (if running in monitoring mode)
- `user_agent`: Browser user agent string (change only if experiencing issues)

### Example Configurations

1. To change the price range to $3,500-$5,000:
```json
"filters": {
  "price_range": [3500, 5000]
}
```

2. To update the apartment URL (if it changes):
```json
"url": "https://www.newurl.com/crescent-village/availability.html"
```

## Usage

Run the script with:
```bash
python irvine_scraper.py
```

The script will:
1. Navigate to the Crescent Village availability page
2. Expand all floor plans
3. Filter for 2 bed/2 bath units
4. Apply price range filter
5. Save matching units to `apartments.csv`

## Output

The script generates an `apartments.csv` file with the following columns:

- **Apartment**: Building name (e.g., Cadiz, Milano)
- **BLDG NO. / APT NO.**: Unit identifier
- **TERM**: Lease term length
- **PRICE**: Monthly rent
- **AVAILABLE**: Availability date
- **Floor**: Floor number
- **FEATURES**: Unit amenities and features

Example output:
```csv
Apartment,BLDG NO. / APT NO.,TERM,PRICE,AVAILABLE,Floor,FEATURES
Milano,03 1282,12 mo.,$3735,04/02/2025,2th Floor,"2nd Floor, Dog Friendly, Elevator, Granite Countertops, Walk-in Closet, Washer & Dryer In Home"
```

## Features Tracked

The script captures various unit features including:
- Floor level
- Corner/End unit status
- Dog-friendly units
- Elevator access
- Flooring type
- Kitchen features (islands, appliances)
- Views (park, pool, courtyard)
- Special amenities (walk-in closets, patios)

## Error Handling

The script includes:
- Robust error handling for network issues
- Detailed logging for troubleshooting
- Graceful handling of missing data
- Automatic retry for failed page loads

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
