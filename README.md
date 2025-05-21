# 🌤️ Weather Forecast App with ML Forecasting

A Streamlit app that shows real-time current weather and 5-day forecast for any city using OpenWeatherMap API.  
Features include temperature, min/max temps, wind speed (km/h), humidity, pressure, air quality index (AQI), and a temperature trend chart.

---

## Setup Instructions

1. Clone this repository  
git clone < https://github.com/Tech-Nomadic-X/weather-forecast-app >
2. Create and activate a virtual environment (recommended)  

python -m venv venv
Windows

venv\Scripts\activate
Linux / Mac

source venv/bin/activate


3. Install dependencies  
pip install -r requirements.txt


4. Replace the API key in `app.py` with your OpenWeatherMap API key

5. Run the app  
streamlit run app.py


---

## Usage

- Enter a city name and press Enter or click “Get Weather”  
- View current weather data, AQI, and 5-day forecast  
- Temperature trend graph for next 5 days included  

---

## Notes

- The app uses the OpenWeatherMap API, so make sure you have a valid API key  
- Wind speed is displayed in km/h  
- Min and max temperatures are accurately calculated from forecast data

---

## License

MIT License
