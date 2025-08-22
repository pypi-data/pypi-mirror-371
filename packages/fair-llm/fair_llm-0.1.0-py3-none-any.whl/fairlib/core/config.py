# fairlib.core.config.py

import yaml
from pathlib import Path
from fairlib.core.config_schemas import AppSettings

def load_settings() -> AppSettings:
    """
    Loads settings from the YAML file and validates them using Pydantic.
    
    Returns:
        An instance of AppSettings containing the application configuration.
        
    Raises:
        FileNotFoundError: If the settings file is not found.
        ValidationError: If the settings file does not match the schema.
    """
    config_path = Path(__file__).parent.parent / "config/settings.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    # Pydantic will automatically validate the data and raise an error if it's invalid
    return AppSettings(**config_data)

# Create a single, validated settings object for the application to import
settings = load_settings()
