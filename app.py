import streamlit as st
import pandas as pd
import joblib
import serial
import time
import numpy as np

# -------------------------------
# 🔌 Serial Connection
# -------------------------------
@st.cache_resource
def init_serial():
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        time.sleep(2)
        return ser
    except Exception as e:
        st.error(f"Serial connection failed: {e}")
        return None

ser = init_serial()

# -------------------------------
# 📡 Read ESP32 Data
# -------------------------------
def read_esp32():
    if ser is None:
        return None

    try:
        if ser.in_waiting == 0:
            return None

        line = ser.readline().decode(errors='ignore').strip()

        if not line:
            return None

        values = line.split(",")

        # Expect 7 values from ESP32
        if len(values) != 7:
            return None

        current = float(values[0])
        rpm = float(values[1])
        temp = float(values[2])
        ax = float(values[3])
        ay = float(values[4])
        az = float(values[5])
        pressure = float(values[6])

        return current, rpm, temp, ax, ay, az, pressure

    except:
        return None

# -------------------------------
# 🤖 Load ML Model
# -------------------------------
model = joblib.load("motor_model.pkl")

# -------------------------------
# 🖥️ UI
# -------------------------------
st.title("⚡ EV Motor Health Monitoring (Live Dashboard)")

placeholder = st.empty()

# -------------------------------
# 🔄 Read Data
# -------------------------------
data = read_esp32()

if data is None:
    placeholder.warning("⚠️ Waiting for ESP32 data...")
    st.stop()

current, rpm, temp, ax, ay, az, pressure = data

# -------------------------------
# ⚙️ Derived Calculations
# -------------------------------
omega = rpm / 9.55  # RPM → rad/s

Kt = 0.1
torque = Kt * current

efficiency = (torque * omega) / (current * rpm + 1e-6)

# Correct vibration magnitude
vibration = np.sqrt(ax**2 + ay**2 + az**2)

# -------------------------------
# 📊 Display Data
# -------------------------------
with placeholder.container():

    st.subheader("📡 Live Sensor Data")

    st.write({
        "Current (A)": current,
        "RPM": rpm,
        "Temperature (°C)": temp,
        "Ax": ax,
        "Ay": ay,
        "Az": az,
        "Pressure (PSI)": pressure,
        "Vibration": vibration
    })

    st.subheader("🧠 Digital Twin Output")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Speed (rad/s)", f"{omega:.2f}")
    col2.metric("Torque (Nm)", f"{torque:.2f}")
    col3.metric("Efficiency", f"{efficiency:.2f}")
    col4.metric("RPM", f"{rpm:.0f}")

# -------------------------------
# 🤖 ML Prediction
# -------------------------------
input_data = pd.DataFrame([{
    "Ambient Temp (°C)": temp,
    "Current (A)": current,
    "Humidity (%)": 50,
    "Motor Speed (RPM)": rpm,
    "Temperature (°C)": temp,
    "Voltage (V)": 12,  # placeholder (since ESP32 not sending voltage)
    "Vibration (g)": vibration
}])

# Align with model features
input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)
input_data = input_data.astype(float)

prediction = model.predict(input_data)[0]

st.subheader("🤖 Prediction")
st.success(f"Motor Condition: {prediction}")

# -------------------------------
# 🔄 Auto Refresh
# -------------------------------
time.sleep(1)
st.rerun()