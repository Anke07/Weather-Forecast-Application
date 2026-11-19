# Weather Forecast Application

A desktop weather application built with **Python** and **Tkinter**. Search for a city to view its current weather conditions and a five-day forecast in a simple graphical interface.

## Features

- Search weather by city name
- Current temperature and feels-like temperature
- Humidity and wind speed
- Weather descriptions and symbols
- Five-day forecast with daily high and low temperatures
- Automatic local time zone for the selected location
- Input validation, network timeouts, and helpful error messages
- Uses the free Open-Meteo APIs; no API key is required

## Tech stack

- Python 3.10+
- Tkinter (Python GUI library)
- Requests (HTTP requests)
- Open-Meteo Geocoding API and Forecast API

## Project structure

```text
weather_forecast_app/
├── main.py             # Tkinter user interface
├── weather_service.py  # City lookup and weather API logic
├── requirements.txt    # Python dependency list
├── .gitignore
└── README.md
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Anand-a4/weather-forecast-app.git
cd weather-forecast-app
```

Replace `YOUR-USERNAME` with your GitHub username and adjust the repository name if needed.

### 2. Create and activate a virtual environment (recommended)

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Tkinter is included with most standard Python installations. On some Linux distributions, install the `python3-tk` system package if Tkinter is missing.

### 4. Run the application

```bash
python main.py
```

Enter a city name, then select **Get Weather**. An internet connection is required to retrieve weather data.

## API information

This project uses:

- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) to convert a city name into coordinates.
- [Open-Meteo Forecast API](https://open-meteo.com/en/docs) to retrieve current conditions and daily forecasts.

The application requests metric units (Celsius and km/h) and uses the location's automatic time zone.

## Troubleshooting

- **City not found:** Check the spelling or try a nearby larger city.
- **Connection error:** Check your internet connection and try again.
- **Tkinter not found:** Install the Tkinter package for your Python installation (for Ubuntu/Debian, `sudo apt install python3-tk`).

## Future improvements

- Add saved/favourite cities
- Add hourly forecasts and weather alerts
- Add unit switching between Celsius/Fahrenheit
- Add a weather map and historical weather view

