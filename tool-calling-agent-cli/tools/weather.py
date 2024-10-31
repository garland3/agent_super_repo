from typing import Dict
import requests
import yaml
import os

# Load API key from secrets.yaml
def load_api_key():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'secrets.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['default']['weatherapi_key']

# Tool specification
TOOL_SPEC = {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
            }
        },
        "required": ["location"]
    }
}

def get_weather(location: str, unit: str = "fahrenheit") -> Dict:
    """
    Get weather information for a location using WeatherAPI.com
    
    Args:
        location (str): City and state (e.g., "San Francisco, CA")
        unit (str): Temperature unit (celsius or fahrenheit)
        
    Returns:
        Dict: Weather information or error message
    """
    try:
        api_key = load_api_key()
        base_url = "https://api.weatherapi.com/v1/current.json"
        
        # Make API request
        params = {
            'key': api_key,
            'q': location,
            'aqi': 'yes'  # Include air quality data
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "location": f"{data['location']['name']}, {data['location']['region']}",
            "temperature": data['current']['temp_f'] if unit == "fahrenheit" else data['current']['temp_c'],
            "unit": unit,
            "condition": data['current']['condition']['text'],
            "humidity": data['current']['humidity'],
            "wind_speed": data['current']['wind_mph'] if unit == "fahrenheit" else data['current']['wind_kph'],
            "wind_unit": "mph" if unit == "fahrenheit" else "kph",
            "feels_like": data['current']['feelslike_f'] if unit == "fahrenheit" else data['current']['feelslike_c'],
            "uv_index": data['current']['uv'],
            "last_updated": data['current']['last_updated']
        }
        
        # Add air quality data if available
        if 'air_quality' in data['current']:
            weather_info['air_quality'] = {
                'us_epa_index': data['current']['air_quality']['us-epa-index'],
                'pm2_5': data['current']['air_quality']['pm2_5'],
                'pm10': data['current']['air_quality']['pm10']
            }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "status": "error"
        }
    except KeyError as e:
        return {
            "error": f"Failed to parse weather data: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "status": "error"
        }
