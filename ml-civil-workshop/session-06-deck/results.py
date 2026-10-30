"""Writes every number the Session 06 deck uses to data/results.json.

Two sources:
  * The instructor's Session 06 notebook: Random Forest, the selected ANN (32, 16) and the four candidate architectures.
    No notebook file was supplied with the draft deck, so these values are copied from the draft's own result charts.
  * The UCI Concrete Compressive Strength data (data/concrete_uci.csv, the original Concrete_Data.xls exported to CSV):
    dataset facts, the 80/20 split and the linear-regression baseline. The baseline reproduces the draft exactly
    (MAE 7.745, RMSE 9.797, R² 0.628 with train_test_split(test_size=0.2, random_state=42)), which confirms the split.

Usage: python3 results.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).parent
FEATURES = ["cement", "slag", "ash", "water", "superplastic", "coarseagg", "fineagg", "age"]

df = pd.read_csv(HERE / "data/concrete_uci.csv")
X, y = df[FEATURES], df["strength"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


def scores(t, p):
    return {"mae": mean_absolute_error(t, p), "rmse": mean_squared_error(t, p) ** 0.5, "r2": r2_score(t, p)}


lin = LinearRegression().fit(X_train, y_train)
p_lin = lin.predict(X_test)

R = {
    "n": len(df), "n_features": len(FEATURES), "missing": int(df.isna().sum().sum()),
    "n_train": len(X_train), "n_test": len(X_test),
    "ranges": {c: [float(df[c].min()), float(df[c].max())] for c in FEATURES + ["strength"]},
    "means": {c: float(X_train[c].mean()) for c in FEATURES}, "sds": {c: float(X_train[c].std(ddof=0)) for c in FEATURES},
    "strength_hist": np.histogram(y, bins=np.arange(0, 90, 5))[0].tolist(),
    "strength_mean": float(y.mean()),
    # notebook results (instructor's draft deck, slides 28, 30, 31)
    "arch": [{"name": "Small", "layers": [8], "rmse": 7.175}, {"name": "Medium", "layers": [16, 8], "rmse": 6.390},
             {"name": "Larger", "layers": [32, 16], "rmse": 5.980}, {"name": "Deeper", "layers": [32, 16, 8], "rmse": 6.381}],
    "test": {"Linear regression": scores(y_test, p_lin),
             "Random forest": {"mae": 3.791, "rmse": 5.571, "r2": 0.880},
             "ANN (32, 16)": {"mae": 4.697, "rmse": 6.042, "r2": 0.858}},
    "lin_test": {"y": y_test.round(2).tolist(), "p": np.round(p_lin, 2).tolist(), "age": X_test["age"].tolist()},
}
nb = {"mae": 7.745, "rmse": 9.797, "r2": 0.628}
assert all(abs(R["test"]["Linear regression"][k] - v) < 6e-4 for k, v in nb.items()), R["test"]["Linear regression"]

(HERE / "data/results.json").write_text(json.dumps(R))
print({k: R[k] for k in ("n", "n_train", "n_test", "missing")}, R["test"]["Linear regression"])
