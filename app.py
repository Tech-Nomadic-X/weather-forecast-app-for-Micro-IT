import streamlit as st
import requests
from datetime import datetime, date
from collections import defaultdict

API_KEY = "91a068e8c7d81d9de08d7b1b717b9114"

st.set_page_config(page_title="☁️ 5-Day Weather Forecast", layout="centered")
st.title("☁️ 5-Day Weather Forecast")

with st.form("weather_form"):
    city = st.text_input("Enter your city")
    st.caption("Press Enter to view the weather")
    search = st.form_submit_button("Get Weather")

# === API CALLERS ===

def get_coordinates(city_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    res = requests.get(url).json()
    if res:
        return res[0]['lat'], res[0]['lon']
    return None, None

def get_current_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_aqi(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    return requests.get(url).json()

def get_aqi_description(index):
    levels = {
        1: "🟢 Good",
        2: "🟡 Fair",
        3: "🟠 Moderate",
        4: "🔴 Poor",
        5: "🔣 Very Poor"
    }
    return levels.get(index, "Unknown")

def extract_daily_forecast(forecast_data):
    daily = {}
    min_max = defaultdict(lambda: {'min': float('inf'), 'max': float('-inf')})

    for entry in forecast_data['list']:
        date_str, time = entry['dt_txt'].split(' ')
        temp_min = entry['main']['temp_min']
        temp_max = entry['main']['temp_max']

        min_max[date_str]['min'] = min(min_max[date_str]['min'], temp_min)
        min_max[date_str]['max'] = max(min_max[date_str]['max'], temp_max)

        if time == "12:00:00" and date_str not in daily:
            daily[date_str] = {
                'temp': entry['main']['temp'],
                'desc': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon'],
                'wind': entry['wind']['speed'] * 3.6,
                'humidity': entry['main']['humidity'],
                'pressure': entry['main']['pressure'],
                'min_temp': temp_min,
                'max_temp': temp_max
            }

    for date_str in daily:
        daily[date_str]['min_temp'] = round(min_max[date_str]['min'], 1)
        daily[date_str]['max_temp'] = round(min_max[date_str]['max'], 1)

    return daily

# === MAIN ===

if search and city:
    lat, lon = get_coordinates(city)

    if lat and lon:
        st.markdown(f"📍 **Location:** {city.title()} ({lat:.4f}, {lon:.4f})")

        with st.spinner("Fetching weather data..."):
            weather = get_current_weather(lat, lon)
            forecast = get_forecast(lat, lon)
            aqi_data = get_aqi(lat, lon)

        # 🔁 Fix Min/Max Temp for Today Using Forecast Data
        today_str = date.today().strftime('%Y-%m-%d')
        today_temps = [
            entry['main']['temp'] 
            for entry in forecast['list'] 
            if entry['dt_txt'].startswith(today_str)
        ]
        today_min = round(min(today_temps), 1) if today_temps else weather['main']['temp']
        today_max = round(max(today_temps), 1) if today_temps else weather['main']['temp']

        # === CURRENT WEATHER ===
        st.subheader("🌤️ Current Weather")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{weather['main']['temp']} °C")
            st.metric("Min Temp", f"{today_min} °C")
            st.metric("Max Temp", f"{today_max} °C")
        with col2:
            st.metric("Humidity", f"{weather['main']['humidity']}%")
            wind_kmh = round(weather['wind']['speed'] * 3.6, 1)
            st.metric("Wind Speed", f"{wind_kmh} km/h")
            st.metric("Pressure", f"{weather['main']['pressure']} hPa")

        # === AQI ===
        st.subheader("🌫️ Air Quality Index")
        aqi_index = aqi_data['list'][0]['main']['aqi']
        aqi_text = get_aqi_description(aqi_index)
        st.markdown(f"**AQI Level:** {aqi_index} - {aqi_text}")

        # === FORECAST ===
        st.subheader("🗕️ 5-Day Forecast")
        daily_forecast = extract_daily_forecast(forecast)

        for date_str, info in daily_forecast.items():
            st.markdown(f"**{datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %d %b')}**")
            col1, col2 = st.columns([1, 3])
            with col1:
                icon_url = f"http://openweathermap.org/img/wn/{info['icon']}@2x.png"
                st.image(icon_url, width=80)
            with col2:
                st.write(f"🌡️ Temp: {info['temp']} °C")
                st.write(f"🔻 Min: {info['min_temp']} °C")
                st.write(f"🔹 Max: {info['max_temp']} °C")
                st.write(f"💨 Wind: {round(info['wind'], 1)} km/h")
                st.write(f"💧 Humidity: {info['humidity']}%")
                st.write(f"🔽 Pressure: {info['pressure']} hPa")
                st.write(f"☁️ {info['desc'].capitalize()}")

        # === TEMP TREND CHART ===
        st.subheader("🔢 Temperature Trend (Next 5 Days)")
        import pandas as pd
        temps = [(entry['dt_txt'], entry['main']['temp']) for entry in forecast['list']]
        df = pd.DataFrame(temps, columns=["datetime", "temp"])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index("datetime")
        st.line_chart(df['temp'])

        # === SUNRISE / SUNSET ===
        st.subheader("🌅 Sunrise and 🌇 Sunset")
        sunrise = datetime.utcfromtimestamp(weather['sys']['sunrise'] + weather['timezone']).strftime('%H:%M')
        sunset = datetime.utcfromtimestamp(weather['sys']['sunset'] + weather['timezone']).strftime('%H:%M')
        st.write(f"Sunrise: {sunrise} AM")
        st.write(f"Sunset: {sunset} PM")

    else:
        st.error("❌ City not found. Please try a different name.")
