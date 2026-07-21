import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import TargetEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os

print("=== BẮT ĐẦU HUẤN LUYỆN VÀ SO SÁNH MÔ HÌNH ===")
dataset_path = "dataset.csv"
if not os.path.exists(dataset_path):
    print(f"Error: Could not find {dataset_path}!")
    exit()

df = pd.read_csv(dataset_path)

# 1. Clean Data
df.drop(columns=[c for c in df.columns if 'Unnamed' in c], inplace=True, errors='ignore')
df.drop_duplicates(subset='track_id', inplace=True)
df.reset_index(drop=True, inplace=True)
df['duration_min'] = df['duration_ms'] / 60_000
df['explicit'] = df['explicit'].astype(int)

# 2. Feature Selection
categorical_features = ['track_genre']
numeric_features = [
    'danceability', 'energy', 'key', 'loudness', 'mode',
    'speechiness', 'acousticness', 'instrumentalness',
    'liveness', 'valence', 'tempo', 'time_signature',
    'explicit', 'duration_min'
]

X = df[categorical_features + numeric_features]
y = df['popularity']

# 3. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Preprocessing for all models
# TargetEncoder uses cross-fitting to avoid leakage
preprocessor = ColumnTransformer(
    transformers=[
        ('target_enc', TargetEncoder(target_type='continuous', random_state=42), categorical_features),
        ('scaler', StandardScaler(), numeric_features) # Scaler is needed for Ridge and KNN
    ],
    remainder='passthrough'
)

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

# 5. Define Models to Compare
models = {
    'Ridge Regression': Ridge(alpha=10),
    'Decision Tree': DecisionTreeRegressor(max_depth=12, random_state=42),
    'AdaBoost': AdaBoostRegressor(n_estimators=50, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
    'XGBoost': xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1),
    'LightGBM': lgb.LGBMRegressor(n_estimators=400, max_depth=8, learning_rate=0.04, random_state=42, n_jobs=-1, verbose=-1)
}

print(f"\nĐang tiến hành huấn luyện {len(models)} thuật toán (sẽ mất một lúc)...")
results = []
best_model_name = None
best_r2 = -float('inf')
best_pipeline = None

print("-" * 65)
print(f"{'Mô hình (Algorithm)':<20} | {'RMSE':<10} | {'MAE':<10} | {'R²':<10}")
print("-" * 65)

for name, model in models.items():
    # Build pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    # Train
    pipeline.fit(X_train, y_train)
    
    # Predict & Evaluate
    preds = pipeline.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    
    # Print result
    print(f"{name:<20} | {rmse:<10.3f} | {mae:<10.3f} | {r2:<10.4f}")
    
    # Save the best model based on R2
    if r2 > best_r2:
        best_r2 = r2
        best_model_name = name
        best_pipeline = pipeline

print("-" * 65)
print(f"\n🏆 Thuật toán tốt nhất được chọn: **{best_model_name}** với R² = {best_r2:.4f}")

# 6. Save the Best Pipeline
joblib.dump(best_pipeline, 'pipeline.pkl')
unique_genres = sorted(df['track_genre'].dropna().unique().tolist())
joblib.dump(unique_genres, 'genres.pkl')

print("Đã lưu tự động mô hình tốt nhất vào pipeline.pkl và danh sách thể loại vào genres.pkl!")
