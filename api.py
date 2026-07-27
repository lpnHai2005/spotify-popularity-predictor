import os
from contextlib import asynccontextmanager

import joblib
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# State — loaded once at startup via lifespan
# ---------------------------------------------------------------------------
app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy resources once at startup, clean up on shutdown."""
    pipeline_path = "pipeline.pkl"
    genres_path = "genres.pkl"

    if os.path.exists(pipeline_path):
        app_state["pipeline"] = joblib.load(pipeline_path)
        print("✅ Model pipeline loaded successfully!")
    else:
        app_state["pipeline"] = None
        print("⚠️  Warning: pipeline.pkl not found. Run train_model.py first.")

    if os.path.exists(genres_path):
        raw = joblib.load(genres_path)
        # Support both old format (list) and new format (dict with genres + model_name)
        if isinstance(raw, dict):
            app_state["genres"]     = raw.get("genres", [])
            app_state["model_name"] = raw.get("model_name", "Machine Learning")
            app_state["r2_score"]   = raw.get("r2_score", None)
        else:
            app_state["genres"]     = raw
            app_state["model_name"] = "Machine Learning"
            app_state["r2_score"]   = None
    else:
        app_state["genres"]     = ["acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime"]
        app_state["model_name"] = "Machine Learning"
        app_state["r2_score"]   = None
        print("⚠️  Warning: genres.pkl not found. Using fallback genre list.")

    yield  # Application runs here

    # Cleanup (if needed)
    app_state.clear()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Spotify Popularity Predictor API",
    version="1.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production via env var
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Schema
# ---------------------------------------------------------------------------
class TrackFeatures(BaseModel):
    track_genre:      str
    danceability:     float = Field(ge=0.0, le=1.0)
    energy:           float = Field(ge=0.0, le=1.0)
    key:              int   = Field(ge=0, le=11)
    loudness:         float = Field(ge=-60.0, le=0.0)
    mode:             int   = Field(ge=0, le=1)
    speechiness:      float = Field(ge=0.0, le=1.0)
    acousticness:     float = Field(ge=0.0, le=1.0)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    liveness:         float = Field(ge=0.0, le=1.0)
    valence:          float = Field(ge=0.0, le=1.0)
    tempo:            float = Field(ge=0.0, le=300.0)
    time_signature:   int   = Field(ge=1, le=7)
    explicit:         int   = Field(ge=0, le=1)
    duration_min:     float = Field(ge=0.0)


# ---------------------------------------------------------------------------
# Helper — replicate the same feature engineering as train_model.py
# ---------------------------------------------------------------------------
def _apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Must mirror every transformation done in train_model.py before pipeline.fit()."""
    # Cyclical key encoding
    df["key_sin"] = np.sin(2 * np.pi * df["key"] / 12)
    df["key_cos"] = np.cos(2 * np.pi * df["key"] / 12)

    # Interaction features
    df["dance_x_energy"]   = df["danceability"] * df["energy"]
    df["valence_x_energy"] = df["valence"]      * df["energy"]
    df["loud_x_energy"]    = df["loudness"]     * df["energy"]

    return df


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Quick health check — useful for deployment monitoring."""
    model_loaded = app_state.get("pipeline") is not None
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
    }


@app.get("/metadata")
def get_metadata():
    """Return genre list and the name of the best-trained model."""
    return {
        "genres":     app_state.get("genres", []),
        "model_name": app_state.get("model_name", "Machine Learning"),
        "r2_score":   app_state.get("r2_score"),
    }


@app.post("/predict")
def predict_popularity(features: TrackFeatures):
    pipeline = app_state.get("pipeline")
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model pipeline is not loaded. Run train_model.py first.",
        )

    try:
        # Build a single-row DataFrame from the raw user input
        input_df = pd.DataFrame([features.model_dump()])

        # Apply the same feature engineering that was done during training
        input_df = _apply_feature_engineering(input_df)

        # Predict
        prediction = pipeline.predict(input_df)[0]

        # Clamp output to [0, 100]
        pred_clamped = float(max(0.0, min(100.0, prediction)))

        return {"predicted_popularity": round(pred_clamped, 2)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Serve Frontend
# ---------------------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    def serve_index():
        return {"message": "Frontend not found. Please create the frontend directory."}


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
