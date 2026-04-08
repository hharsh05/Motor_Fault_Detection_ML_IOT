import numpy as np

def digital_twin_from_sensors(current, rpm, pressure_psi, temperature):
    
    # -------- Convert RPM to angular speed --------
    omega = (rpm * 2 * np.pi) / 60  # rad/s

    # -------- Estimate motor constants (normalized approach) --------
    # Since voltage is removed, we approximate Ke using speed-current relation
    Ke = omega / (current + 1e-6)

    # Torque constant (approx equal to Ke)
    Kt = Ke

    # Motor resistance estimation (relative model)
    R = 1.0 / (current + 1e-6)

    # Friction coefficient (tunable)
    B = 0.01

    # -------- Load torque estimation --------
    # Pressure influences mechanical load (tunable mapping)
    load_torque = pressure_psi * 0.1

    # -------- Temperature effect factor --------
    # Higher temperature → higher resistance → efficiency drop
    temp_factor = 1 + (temperature - 25) * 0.005

    # -------- Speed estimation --------
    omega_est = (omega) / temp_factor

    # -------- Current estimation --------
    current_est = current * temp_factor

    # -------- Torque --------
    torque = Kt * current

    # -------- Efficiency --------
    efficiency = (torque * omega) / ((current * R) + 1e-6)

    return {
        "rpm": rpm,
        "omega_rad_s": omega,
        "current": current,
        "temperature": temperature,
        "pressure_psi": pressure_psi,
        "Ke_est": Ke,
        "Kt_est": Kt,
        "resistance_est": R,
        "load_torque": load_torque,
        "torque": torque,
        "estimated_speed": omega_est,
        "estimated_current": current_est,
        "efficiency": efficiency
    }