from pathlib import Path
from typing import Any
import json

# Get the absolute path of config.json
CONFIG_PATH = Path(__file__).parent / "config.json"

# Load the JSON configuration
def load_config() -> Any:
    """
    Load the JSON configuration from config.json
    """
    with CONFIG_PATH.open("r") as file:
        return json.load(file)