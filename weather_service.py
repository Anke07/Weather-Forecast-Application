"""Functions for retrieving weather and location data from Open-Meteo."""

from typing import Any

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 12


class WeatherServiceError(Exception):
    """Raised when a city cannot be found or weather data is unavailable."""


def weather_description(code: int) -> tuple[str, str]:
    """Convert a WMO weather code into a readable description and symbol."""
    descriptions = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Moderate drizzle", "🌦️"),
        55: ("Dense drizzle", "🌧️"),
        56: ("Light freezing drizzle", "🌧️"),
        57: ("Dense freezing drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"),
        63: ("Moderate rain", "🌧️"),
        65: ("Heavy rain", "🌧️"),
        66: ("Light freezing rain", "🌧️"),
        67: ("Heavy freezing rain", "🌧️"),
        71: ("Slight snow", "🌨️"),
        73: ("Moderate snow", "🌨️"),
        75: ("Heavy snow", "❄️"),
        77: ("Snow grains", "❄️"),
        80: ("Slight rain showers", "🌦️"),
        81: ("Moderate rain showers", "🌧️"),
        82: ("Violent rain showers", "⛈️"),
        85: ("Slight snow showers", "🌨️"),
        86: ("Heavy snow showers", "❄️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with hail", "⛈️"),
        99: ("Thunderstorm with heavy hail", "⛈️"),
    }
    return descriptions.get(code, ("Unknown conditions", "🌡️"))


class WeatherService:
    """Looks up a city and requests its current weather and daily forecast."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "WeatherForecastDesktop/1.0"})

    def get_weather(self, city: str) -> dict[str, Any]:
        location_response = self.session.get(
            GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=TIMEOUT_SECONDS,
        )
        location_response.raise_for_status()
        locations = location_response.json().get("results", [])
        if not locations:
            raise WeatherServiceError(f"No location found for '{city}'. Check the spelling and try again.")

        location = locations[0]
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 5,
            "wind_speed_unit": "kmh",
        }
        weather_response = self.session.get(FORECAST_URL, params=params, timeout=TIMEOUT_SECONDS)
        weather_response.raise_for_status()
        payload = weather_response.json()
        if "current" not in payload or "daily" not in payload:
            raise WeatherServiceError("The weather service returned incomplete data. Please try again.")

        return {
            "location": {
                "name": location.get("name", city),
                "country": location.get("country", ""),
                "admin1": location.get("admin1", ""),
            },
            "current": payload["current"],
            "daily": payload["daily"],
        }
