import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
df = pd.read_csv("NEV_fault_dataset.csv")

# Example: adjust columns based on your dataset
X = df.drop("fault", axis=1)
y = df["fault"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "motor_model.pkl")

print("Model trained and saved!")