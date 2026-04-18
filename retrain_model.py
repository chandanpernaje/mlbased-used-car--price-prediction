import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import joblib

# Load the dataset
print("Loading dataset...")
df = pd.read_csv("Car_details.csv")

# Data Cleaning functions
def clean_mileage(value):
    if pd.isna(value) or value == '':
        return np.nan
    value = str(value)
    match = re.search(r'(\d+\.?\d*)', value)
    return float(match.group(1)) if match else np.nan

def clean_engine(value):
    if pd.isna(value) or value == '':
        return np.nan
    value = str(value)
    match = re.search(r'(\d+)', value)
    return float(match.group(1)) if match else np.nan  

def clean_max_power(value):
    if pd.isna(value) or value == '':
        return np.nan
    value = str(value)
    match = re.search(r'(\d+\.?\d*)', value)
    return float(match.group(1)) if match else np.nan

def clean_torque(value):
    if pd.isna(value) or value == '':
        return np.nan
    value = str(value)
    match = re.search(r'(\d+\.?\d*)', value)
    return float(match.group(1)) if match else np.nan    

# Apply cleaning
df['mileage'] = df['mileage'].apply(clean_mileage)
df['engine'] = df['engine'].apply(clean_engine)
df['max_power'] = df['max_power'].apply(clean_max_power)
df['torque_value'] = df['torque'].apply(clean_torque)

# Handle missing values
df['mileage'].fillna(df['mileage'].median(), inplace=True)
df['engine'].fillna(df['engine'].median(), inplace=True)
df['max_power'].fillna(df['max_power'].median(), inplace=True)
df['torque_value'].fillna(df['torque_value'].median(), inplace=True)
df['seats'].fillna(df['seats'].mode()[0], inplace=True)

# Feature Engineering
df['brand'] = df['name'].astype(str).str.split().str[0]
df['car_age'] = 2024 - df['year']
df['power_to_weight'] = df['max_power'] / df['engine'] * 1000
df['mileage_efficiency'] = df['mileage'] / df['engine'] * 1000

# Encode categorical variables
categorical_cols = ['brand','fuel', 'seller_type', 'transmission', 'owner']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Define features and target
feature_columns = [
    'brand_encoded','car_age', 'km_driven', 'fuel_encoded', 'seller_type_encoded', 
    'transmission_encoded', 'owner_encoded', 'mileage', 'engine', 
    'max_power', 'seats', 'torque_value', 'power_to_weight', 'mileage_efficiency'
]
X = df[feature_columns]
y = df['selling_price']

# Split the data (optional but good practice, here we train on all if we want best prod model, but let's follow notebook)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Feature scaling
scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)

# Train Gradient Boosting (Best model according to notebook)
print("Training Gradient Boosting model...")
model = GradientBoostingRegressor(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# Save the model and preprocessing components
print("Saving models...")
joblib.dump(model, "best_car_price_model.pkl")
joblib.dump(scaler, "car_price_scaler.pkl")
joblib.dump(label_encoders, "label_encoders.pkl")
joblib.dump(feature_columns, "feature_columns.pkl")

print("Done! Models regenerated successfully.")
