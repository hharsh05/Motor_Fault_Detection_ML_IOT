import numpy as np

def digital_twin(V, R, Ke, Kt, B, load_torque):
    # Speed estimation (simplified)
    omega = (V / Ke) * 0.8

    # Current calculation
    current = (V - Ke * omega) / R

    # Torque
    torque = Kt * current

    # Efficiency (approx)
    efficiency = (torque * omega) / (V * current + 1e-6)

    return {
        "speed": omega,
        "current": current,
        "torque": torque,
        "efficiency": efficiency
    }