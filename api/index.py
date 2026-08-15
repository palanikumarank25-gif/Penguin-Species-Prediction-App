from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel  # pyright: ignore[reportMissingImports]
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Penguin Species Prediction API",
    description="API for predicting penguin species using Random Forest",
    version="1.0.0"
)


# --------------------------------------------------
# Request Data Model
# --------------------------------------------------

class PenguinInput(BaseModel):
    island: str
    sex: str
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float


# --------------------------------------------------
# Dataset
# --------------------------------------------------

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "dataprofessor/data/master/penguins_cleaned.csv"
)


# --------------------------------------------------
# Train Random Forest Model
# --------------------------------------------------

def train_model():

    # Load dataset
    df = pd.read_csv(DATA_URL)

    # Separate features and target
    X = df.drop("species", axis=1)
    y = df["species"]

    # Encode categorical features
    X = pd.get_dummies(
        X,
        columns=["island", "sex"]
    )

    # Handle missing values
    X = X.fillna(0)

    # Encode target
    target_mapper = {
        "Adelie": 0,
        "Chinstrap": 1,
        "Gentoo": 2
    }

    y = y.map(target_mapper)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model, X.columns


# --------------------------------------------------
# Home Endpoint
# --------------------------------------------------

@app.get("/api")
def home():

    return {
        "message": "Penguin Species Prediction API is running",
        "docs": "/docs",
        "health": "/api/health",
        "prediction": "/api/predict"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Penguin Prediction
# --------------------------------------------------

@app.post("/api/predict")
def predict_penguin(data: PenguinInput):

    # Train model
    model, feature_columns = train_model()

    # Create input DataFrame
    input_df = pd.DataFrame({
        "island": [data.island],
        "bill_length_mm": [data.bill_length_mm],
        "bill_depth_mm": [data.bill_depth_mm],
        "flipper_length_mm": [data.flipper_length_mm],
        "body_mass_g": [data.body_mass_g],
        "sex": [data.sex]
    })

    # Encode categorical features
    input_df = pd.get_dummies(
        input_df,
        columns=["island", "sex"]
    )

    # Make input columns exactly match
    # training columns
    input_df = input_df.reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Make prediction
    prediction = model.predict(input_df)[0]

    # Prediction probabilities
    probabilities = model.predict_proba(input_df)[0]

    # Convert prediction back to species name
    species_mapper = {
        0: "Adelie",
        1: "Chinstrap",
        2: "Gentoo"
    }

    predicted_species = species_mapper[prediction]

    # Return response
    return {
        "predicted_species": predicted_species,
        "probabilities": {
            "Adelie": round(float(probabilities[0]), 4),
            "Chinstrap": round(float(probabilities[1]), 4),
            "Gentoo": round(float(probabilities[2]), 4)
        }
    }