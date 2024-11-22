import streamlit as st
import requests
import json
import random  # Importing the random library to generate random values

# Set page title and layout
st.set_page_config(page_title="Automated Irrigation System", layout="wide")

# Display a header
st.title("Automated Irrigation System Dashboard")

# Generate random values for testing purposes
soil_moisture = random.randint(0, 100)  # Random value between 0 and 100
light_intensity = random.randint(1, 100000)  # Random value between 1 and 100000 Lux
solar_power = random.choice([True, False])  # Randomly choose between True (Yes) and False (No)
daylight = random.choice([True, False])  # Randomly choose between True (Yes) and False (No)

# Display the random values in the app
st.write(f"**Randomly Generated Values:**")
st.write(f"**Soil Moisture:** {soil_moisture}%")
st.write(f"**Light Intensity:** {light_intensity} Lux")
st.write(f"**Solar Power Available:** {'Yes' if solar_power else 'No'}")
st.write(f"**Daylight:** {'Yes' if daylight else 'No'}")

# Form for entering sensor data
with st.form(key="sensor_data_form"):
    soil_moisture_input = st.slider("Soil Moisture (%)", 0, 100, soil_moisture)
    light_intensity_input = st.slider("Light Intensity (Lux)", 1, 100000, light_intensity)
    solar_power_input = st.radio("Solar Power Available?", ("Yes", "No"), index=1 if solar_power else 0)
    daylight_input = st.radio("Daylight?", ("Yes", "No"), index=1 if daylight else 0)
    
    # Convert the Solar Power and Daylight to boolean
    solar_power_input = True if solar_power_input == "Yes" else False
    daylight_input = True if daylight_input == "Yes" else False

    submit_button = st.form_submit_button(label="Send Data")

# If the form is submitted, send the data to the Flask backend
if submit_button:
    # API endpoint URL (Flask backend running on localhost)
    api_url = "http://127.0.0.1:5000/api/data"
    
    # Prepare the payload to be sent
    payload = {
        "soilMoisture": soil_moisture_input,
        "lightIntensity": light_intensity_input,
        "solarPower": solar_power_input,
        "daylight": daylight_input
    }
    
    # Send the POST request to the Flask backend
    response = requests.post(api_url, json=payload)

    # Handle the response
    if response.status_code == 201:
        st.success(f"Data received successfully. Irrigation Status: {response.json()['irrigationStatus']}")
    else:
        st.error("Failed to send data to the server.")

# Fetch the latest sensor data and irrigation status
status_response = requests.get("http://127.0.0.1:5000/api/status")
if status_response.status_code == 200:
    data = status_response.json()
    
    # Display the most recent data in a dashboard
    st.subheader("Latest Sensor Data")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Soil Moisture", f"{data['soilMoisture']}%", delta_color="inverse")
        st.metric("Light Intensity", f"{data['lightIntensity']} Lux")
        st.metric("Solar Power Available", "Yes" if data['solarPower'] else "No")
    
    with col2:
        st.metric("Daylight", "Yes" if data['daylight'] else "No")
        st.metric("Timestamp", data['timestamp'])

    # Display the irrigation status
    st.subheader("Irrigation Status")
    irrigation_status = "Irrigation Started" if data['soilMoisture'] < 40 and data['daylight'] and data['solarPower'] else "Irrigation Stopped"
    st.write(irrigation_status)

else:
    st.error("Unable to fetch the latest data.")
