import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from twin import digital_twin
from alert import send_whatsapp_alert

# Load ML model
model = joblib.load("motor_model.pkl")

st.title("⚡ EV Motor Digital Twin + ML Health Monitoring")

# --- Sidebar Parameters (Datasheet) ---
st.sidebar.header("Motor Parameters")
R = st.sidebar.slider("Resistance (Ohm)", 0.1, 5.0, 1.0)
Ke = st.sidebar.slider("Back EMF (Ke)", 0.01, 1.0, 0.1)
Kt = st.sidebar.slider("Torque Constant (Kt)", 0.01, 1.0, 0.1)
B = st.sidebar.slider("Friction Coefficient", 0.001, 0.1, 0.01)

# --- Inputs (simulate IoT) ---
st.header("📡 Live Motor Inputs")
V = st.slider("Voltage", 0, 100, 48)
load_torque = st.slider("Load Torque", 0.0, 10.0, 2.0)

# Digital Twin
twin_output = digital_twin(V, R, Ke, Kt, B, load_torque)

# Extract values
omega = twin_output["speed"]
current = twin_output["current"]
torque = twin_output["torque"]
efficiency = twin_output["efficiency"]

# Debug (optional)
#st.write(type(torque))  # should be float

# ML input
input_data = pd.DataFrame([{
    "Ambient Temp (°C)": 30,
    "Current (A)": current,
    "Humidity (%)": 50,
    "Motor Speed (RPM)": omega * 9.55,
    "Temperature (°C)": 40,
    "Voltage (V)": V,
    "Vibration (g)": abs(torque) * 0.05
}])
input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)
input_data = input_data.astype(float)

prediction = model.predict(input_data)[0]

st.subheader("🤖 ML Prediction")
st.write(f"Motor Condition: {prediction}")

# --- Alert System ---
if prediction != "normal":
    st.error("⚠️ Fault Detected!")

    if st.button("Send WhatsApp Alert"):
        sid = send_whatsapp_alert(f"ALERT! Motor Fault Detected: {prediction}")
        st.success(f"Alert sent! SID: {sid}")

# --- Visualization ---
st.subheader("📈 Speed Response")

time = np.linspace(0, 10, 100)
speed_curve = twin_output["speed"] * (1 - np.exp(-time))

fig, ax = plt.subplots()
ax.plot(time, speed_curve)
ax.set_xlabel("Time")
ax.set_ylabel("Speed")
ax.set_title("Motor Speed Response")

st.pyplot(fig)