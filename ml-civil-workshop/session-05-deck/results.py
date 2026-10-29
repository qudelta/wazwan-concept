"""Runs the Session 05 notebook's modelling steps and writes every number the deck uses to data/results.json.

Run with scikit-learn 1.5/1.6: those versions reproduce the instructor notebook's saved outputs exactly, including the
Random Forest (newer releases choose different Random Forest hyperparameters on this grid). charts.py and build.py only
read the JSON, so the deck can be rebuilt without scikit-learn.

Usage: python3 results.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).parent
assert sklearn.__version__.startswith(("1.5", "1.6")), f"use scikit-learn 1.5/1.6 to match the notebook (found {sklearn.__version__})"
RS = 42

# ------------------------------------------------------------------ data, exactly as in the notebook
raw = pd.read_excel(HERE / "data/Simplified_static_dataset_616.xlsx")
df = raw.copy()
df.columns = [str(c).strip() for c in df.columns]
df = df[["itr", "Beta", "CbygammaH", "phi", "fmp"]].rename(
    columns={"Beta": "beta_deg", "CbygammaH": "c_by_gammaH", "phi": "phi_deg", "fmp": "fos"})
df["unstable"] = (df["fos"] < 1.0).astype(int)
FEATURES = ["beta_deg", "c_by_gammaH", "phi_deg"]
X, y = df[FEATURES], df["unstable"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=RS, stratify=y)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RS)

R = {"sklearn": sklearn.__version__}
R["n"], R["n_raw_cols"] = len(df), raw.shape[1]
R["levels"] = {c: sorted(float(v) for v in df[c].unique()) for c in FEATURES}
R["fos_min"], R["fos_max"] = float(df.fos.min()), float(df.fos.max())
R["fos_eq_1"] = int(np.isclose(df.fos, 1.0).sum())
R["counts"] = {str(t): {"below": int((df.fos < t).sum()), "above": int((df.fos >= t).sum())} for t in (1.0, 1.5)}
R["dups"] = int(df.duplicated(FEATURES).sum())
R["missing"] = int(df[FEATURES + ["fos"]].isna().sum().sum())
R["split"] = {"train": len(X_train), "test": len(X_test),
              "train_unstable": int(y_train.sum()), "test_unstable": int(y_test.sum())}
R["fos_hist"] = np.histogram(df.fos, bins=25)[0].tolist()
R["fos_edges"] = np.histogram(df.fos, bins=25)[1].tolist()
R["slice25"] = df[df.phi_deg == 25].sort_values(["c_by_gammaH", "beta_deg"])[["beta_deg", "c_by_gammaH", "fos"]].values.tolist()
R["unstable_by_phi"] = {str(int(p)): int(g.unstable.sum()) for p, g in df.groupby("phi_deg")}

# ------------------------------------------------------------------ illustrative demo from Part A of the notebook
rng = np.random.default_rng(RS)
x_demo = np.linspace(-3, 3, 180)
p_demo = 1 / (1 + np.exp(-1.5 * (x_demo - 0.25)))
y_demo = rng.binomial(1, p_demo)
lin_demo = LinearRegression().fit(x_demo.reshape(-1, 1), y_demo)
log_demo = LogisticRegression().fit(x_demo.reshape(-1, 1), y_demo)
xx = np.linspace(-3.5, 3.5, 141).reshape(-1, 1)
R["demo"] = {"x": x_demo.tolist(), "y": y_demo.tolist(), "xx": xx[:, 0].tolist(),
             "lin": lin_demo.predict(xx).tolist(), "log": log_demo.predict_proba(xx)[:, 1].tolist()}

# ------------------------------------------------------------------ baseline, tuning, test (notebook cells 27-34)
dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
models = {
    "Logistic regression": (Pipeline([("scale", StandardScaler()), ("model", LogisticRegression(max_iter=5000, random_state=RS))]),
                            {"model__C": [.1, 1., 10.], "model__class_weight": [None, "balanced"]}),
    "Decision tree": (DecisionTreeClassifier(random_state=RS),
                      {"max_depth": [2, 3, 4, 5, None], "min_samples_leaf": [1, 3, 5, 10], "class_weight": [None, "balanced"]}),
    "Random forest": (RandomForestClassifier(n_estimators=100, random_state=RS, n_jobs=1),
                      {"max_depth": [None, 4, 8], "min_samples_leaf": [1, 3, 5], "max_features": ["sqrt", 1.0],
                       "class_weight": [None, "balanced"]}),
}
best, R["cv"] = {}, {}
for name, (est, grid) in models.items():
    gs = GridSearchCV(est, grid, scoring="recall", cv=cv, refit=True, n_jobs=1).fit(X_train, y_train)
    best[name] = gs.best_estimator_
    R["cv"][name] = {"recall": float(gs.best_score_), "params": {k.replace("model__", ""): v for k, v in gs.best_params_.items()}}


def evaluate(model):
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
    return {"acc": accuracy_score(y_test, pred), "bal": balanced_accuracy_score(y_test, pred),
            "prec": precision_score(y_test, pred, zero_division=0), "rec": recall_score(y_test, pred, zero_division=0),
            "f1": f1_score(y_test, pred, zero_division=0), "auc": roc_auc_score(y_test, prob),
            "ap": average_precision_score(y_test, prob), "cm": [int(tn), int(fp), int(fn), int(tp)]}


R["test"] = {"Majority baseline": evaluate(dummy), **{n: evaluate(m) for n, m in best.items()}}

# class_weight: effect on logistic regression in CV (out-of-fold predictions on the training set)
R["cw"] = {}
for cw in (None, "balanced"):
    m = Pipeline([("scale", StandardScaler()), ("model", LogisticRegression(C=0.1, class_weight=cw, max_iter=5000, random_state=RS))])
    oof = cross_val_predict(m, X_train, y_train, cv=cv)
    tn, fp, fn, tp = confusion_matrix(y_train, oof).ravel()
    R["cw"][str(cw)] = {"rec": tp / (tp + fn), "prec": tp / (tp + fp), "cm": [int(tn), int(fp), int(fn), int(tp)]}

# probability threshold trade-off, on out-of-fold training probabilities (never the test set)
lr = best["Logistic regression"]
oofp = cross_val_predict(lr, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
R["thr"] = []
for t in (0.3, 0.5, 0.7, 0.9):
    pred = (oofp >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_train, pred).ravel()
    R["thr"].append({"t": t, "rec": tp / (tp + fn), "prec": tp / (tp + fp) if tp + fp else 0.0, "cm": [int(tn), int(fp), int(fn), int(tp)]})
R["oof_prob"] = {"stable": np.sort(oofp[y_train.values == 0]).tolist(), "unstable": np.sort(oofp[y_train.values == 1]).tolist()}

# fitted logistic regression in original units: z = b0 + b·x  (undo the scaler)
sc, lm = lr.named_steps["scale"], lr.named_steps["model"]
w = lm.coef_[0] / sc.scale_
b0 = float(lm.intercept_[0] - (lm.coef_[0] * sc.mean_ / sc.scale_).sum())
R["lr_coef"] = {"b0": b0, **{f: float(v) for f, v in zip(FEATURES, w)}}
R["lr_coef_std"] = {f: float(v) for f, v in zip(FEATURES, lm.coef_[0])}
# a real worked example from the test set: an unstable slope the model flags
probs = lr.predict_proba(X_test)[:, 1]
cand = [i for i in range(len(X_test)) if y_test.iloc[i] == 1 and 0.6 < probs[i] < 0.95]
i = cand[0] if cand else int(np.argmax(probs))
row = X_test.iloc[i]
R["example"] = {**{f: float(row[f]) for f in FEATURES}, "fos": float(df.loc[X_test.index[i], "fos"]),
                "z": float(b0 + sum(w[k] * row[f] for k, f in enumerate(FEATURES))), "p": float(probs[i])}

# decision regions of the three tuned models on the phi = 25 degree slice (fine grid)
bg, cg = np.linspace(15, 65, 101), np.linspace(0, 0.30, 61)
G = pd.DataFrame([(b, c, 25.0) for c in cg for b in bg], columns=FEATURES)
R["regions"] = {"beta": bg.tolist(), "c": cg.tolist(),
                **{n: m.predict(G).reshape(len(cg), len(bg)).tolist() for n, m in best.items()}}

# ------------------------------------------------------------------ appendix numbers (Appendix A notebook)
rng = np.random.default_rng(RS)
R["bootstrap"] = rng.choice(np.arange(12), size=12, replace=True).tolist()

(HERE / "data/results.json").write_text(json.dumps(R))
for k in ("cv", "test", "cw", "thr", "lr_coef", "example", "split", "counts", "unstable_by_phi"):
    print(k, R[k])
