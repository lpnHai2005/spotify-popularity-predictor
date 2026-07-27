# 🎵 Spotify Track Popularity Predictor (End-to-End ML Pipeline)

![Spotify](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![HTML/CSS/JS](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)

An end-to-end Machine Learning web application designed to predict the popularity of a track on Spotify based **purely on its audio features** (danceability, acousticness, tempo, key, etc.). 

## 🧠 What I Learned & Demonstrated (For Recruiters)

This project was built to showcase a complete transition from a raw Jupyter Notebook to a production-ready Web API, emphasizing strict ML engineering practices:

### 1. Eliminating Bias & The "Cold-Start" Problem
I deliberately removed the `primary_artist` feature from the dataset. While predicting popularity using the artist's name yields artificially high accuracy (due to the artist's existing fame), it introduces a severe **Cold-Start Problem** for new/indie artists. By forcing the model to rely *only* on musical theory and audio signals, the pipeline ensures unbiased evaluation of the song itself.

### 2. Preventing Data Leakage 
A common pitfall in ML is target-encoding categorical variables (like `track_genre`) across the entire dataset before splitting. I constructed a `scikit-learn Pipeline` utilizing cross-fitting `TargetEncoder` integrated within a `ColumnTransformer` to guarantee zero target leakage between the train and test sets.

### 3. Automated Model Selection (AutoML-lite)
Instead of hardcoding a single algorithm, the training script (`train_model.py`) acts as a benchmarking suite. It automatically trains and evaluates 6 different models (Ridge, Decision Tree, AdaBoost, Random Forest, XGBoost, LightGBM) and dynamically serializes the best-performing pipeline into `pipeline.pkl`.

### 4. Full-Stack Deployment
Bridged the gap between Data Science and Software Engineering by deploying the `.pkl` model via a highly performant **FastAPI** backend, consumed by a custom-built, responsive "Spotify-themed" Vanilla JS frontend (featuring Glassmorphism and CSS animations).

## 📊 Model Evaluation & Benchmarking

The model was trained on a dataset of over 114,000 Spotify tracks across 114 different genres. Below is the automated benchmarking result on a 20% hold-out test set:

| Algorithm | RMSE | MAE | R² | Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| Ridge Regression | 16.853 | 12.031 | 0.3200 | ~1 |
| Decision Tree | 17.086 | 11.713 | 0.3011 | ~3 |
| AdaBoost | 17.388 | 13.387 | 0.2762 | ~8 |
| **Random Forest** | **15.997** | **11.261** | **0.3873** | ~45 |
| XGBoost | 16.058 | 11.392 | 0.3826 | ~30 |
| LightGBM | 16.156 | 11.467 | 0.3751 | ~15 |

> **Note on R² Score**: An R² of ~0.38 is considered highly realistic and robust for this specific domain. Predicting human musical taste based *solely* on raw audio numbers (without artist hype or marketing budgets) is notoriously difficult. The training script benchmarks all 6 models and **automatically serializes the winner** — the frontend dynamically reads the model name from the API.
## 🛠️ Architecture & Workflow

1.  **`notebooks/spotify_eda_analysis.ipynb`**: The Research Phase. Contains deep Exploratory Data Analysis (EDA) with professional statistical charts, correlation matrices, and density plots to understand the data before modeling. Included with detailed professional insights in Vietnamese.
2.  **`train_model.py`**: The Production Training script. Cleans the data, runs the benchmarking suite, constructs the pipeline, and saves the best model.
3.  **`api.py`**: The FastAPI application serving predictions via `POST /predict` and dynamically providing metadata via `GET /metadata`.
4.  **`frontend/`**: The Spotify-Clone UI utilizing raw HTML/CSS/JS for zero-dependency high performance.

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
```

> **Dataset**: `dataset.csv` from [Kaggle — Spotify Tracks Dataset](https://www.kaggle.com/datasets/yashdev01/spotify-tracks-dataset).

> **Note**: `dataset.csv` (~20 MB) and `pipeline.pkl` (~24 MB) are excluded from version control via `.gitignore`.

### 1. Train the Model
Ensure `dataset.csv` is in the root directory, then run:
```bash
python train_model.py
```

### 2. Run the Web App
Start the FastAPI server:
```bash
python api.py
```

### 3. Open the App
Go to your browser and open **[http://localhost:8000](http://localhost:8000)**.

> **Note**: The terminal will show `Uvicorn running on http://0.0.0.0:8000` — this is normal. `0.0.0.0` means the server listens on all network interfaces. Always use `localhost:8000` (or `127.0.0.1:8000`) in your browser.

---
*Developed as a demonstration of production-grade Machine Learning Engineering.*
