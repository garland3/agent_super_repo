from typing import Dict
import requests
import yaml
import os

# Load API key from secrets.yaml
def load_api_key():
    print("[DEBUG] Loading API key from secrets.yaml")
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'secrets.yaml')
    print(f"[DEBUG] Config path: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print("[DEBUG] API key loaded successfully")
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
        print(f"[DEBUG] Getting weather for location: {location}, unit: {unit}")
        api_key = load_api_key()
        base_url = "https://api.weatherapi.com/v1/current.json"
        
        # Make API request
        params = {
            'key': api_key,
            'q': location,
            'aqi': 'yes'  # Include air quality data
        }
        
        print(f"[DEBUG] Making API request to: {base_url}")
        print(f"[DEBUG] Request parameters (excluding API key): {{'q': {params['q']}, 'aqi': {params['aqi']}}}")
        
        response = requests.get(base_url, params=params)
        print(f"[DEBUG] Response status code: {response.status_code}")
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        print("[DEBUG] Successfully parsed JSON response")
        
        # Extract relevant weather information
        print("[DEBUG] Extracting weather information")
        temp_value = data['current']['temp_f'] if unit == "fahrenheit" else data['current']['temp_c']
        feels_like_value = data['current']['feelslike_f'] if unit == "fahrenheit" else data['current']['feelslike_c']
        print(f"[DEBUG] Temperature: {temp_value} {unit}")
        print(f"[DEBUG] Feels like: {feels_like_value} {unit}")
        
        weather_info = {
            "location": f"{data['location']['name']}, {data['location']['region']}",
            "temperature": temp_value,
            "unit": unit,
            "condition": data['current']['condition']['text'],
            "humidity": data['current']['humidity'],
            "wind_speed": data['current']['wind_mph'] if unit == "fahrenheit" else data['current']['wind_kph'],
            "wind_unit": "mph" if unit == "fahrenheit" else "kph",
            "feels_like": feels_like_value,
            "uv_index": data['current']['uv'],
            "last_updated": data['current']['last_updated']
        }
        
        # Add air quality data if available
        if 'air_quality' in data['current']:
            print("[DEBUG] Air quality data available, adding to response")
            weather_info['air_quality'] = {
                'us_epa_index': data['current']['air_quality']['us-epa-index'],
                'pm2_5': data['current']['air_quality']['pm2_5'],
                'pm10': data['current']['air_quality']['pm10']
            }
            print(f"[DEBUG] Air quality EPA index: {weather_info['air_quality']['us_epa_index']}")
        else:
            print("[DEBUG] No air quality data available")
        
        print("[DEBUG] Successfully compiled weather information")
        return weather_info
        
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] API request failed with error: {str(e)}")
        return {
            "error": f"API request failed: {str(e)}",
            "status": "error"
        }
    except KeyError as e:
        print(f"[DEBUG] Failed to parse weather data. Missing key: {str(e)}")
        print(f"[DEBUG] Available data keys: {data.keys() if 'data' in locals() else 'No data available'}")
        return {
            "error": f"Failed to parse weather data: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"[DEBUG] Unexpected error occurred: {str(e)}")
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "status": "error"
        }
