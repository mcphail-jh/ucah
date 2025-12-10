import pandas as pd
import numpy as np
import pickle
from smt.surrogate_models import KRG
from kriging2pkl import run_kriging

# --- Input/Output File Names ---
data_csv = "data_table.csv"  # single CSV with all params + cl, cd, cm
models_out = {
    "cl": "krg_cl.pkl",
    "cd": "krg_cd.pkl",
    "cm": "krg_cm.pkl",
}

# --- Load CSV ---
df = pd.read_csv(data_csv, header=0)
print("Full data shape (with case name column):", df.shape)

# --- Identify columns ---
n_params = 2
param_cols = df.columns[1:1 + n_params]  # skip case name column
aero_cols = ["cl", "cd", "cm"]

# --- Basic checks ---
if not all(c in df.columns for c in aero_cols):
    raise ValueError(f"CSV must contain aerodynamic columns: {aero_cols}")

# --- Split data ---
X = df[param_cols].to_numpy(dtype=float)  # shape (n_cases, 15)
Y = df[aero_cols].to_numpy(dtype=float)   # shape (n_cases, 3)

print("Processed X shape (n_samples, n_params):", X.shape)
print("Processed Y shape (n_samples, n_outputs):", Y.shape)

# --- Train Kriging models ---
krg_options = dict(theta0=[1e-2]*X.shape[1], hyper_opt="Cobyla")

trained_models = {}
for i, col in enumerate(aero_cols):
    y_vec = Y[:, i]
    print(f"\nTraining KRG for {col} ...")
    sm = KRG(**krg_options)
    sm.set_training_values(X, y_vec)
    sm.train()
    trained_models[col] = sm

    # Save model
    with open(models_out[col], "wb") as f:
        pickle.dump(sm, f)
    print(f"Saved {col} model to {models_out[col]}")


# =======================================================================
# === OPTIMIZATION OF L/D USING TRAINED KRG MODELS ======================
# =======================================================================

import pickle
from scipy.optimize import differential_evolution, minimize

# --- Load the trained cl and cd Kriging models ---
with open(models_out["cl"], "rb") as f:
    krg_cl = pickle.load(f)
with open(models_out["cd"], "rb") as f:
    krg_cd = pickle.load(f)

# --- Use same training data for parameter bounds ---
X_train = X  # from earlier in script (shape: 50 x 15)
bounds = [(np.min(X_train[:, j]), np.max(X_train[:, j])) for j in range(X_train.shape[1])]
print("\nParameter bounds (from training data):")
for i, (lo, hi) in enumerate(bounds):
    print(f"  Param {i+1}: {lo:.6f} – {hi:.6f}")

# --- Define predictor and objective ---
def predict_L_over_D(x):
    x = np.atleast_2d(x)
    cl = krg_cl.predict_values(x).flatten()
    cd = krg_cd.predict_values(x).flatten()
    cd = np.maximum(cd, 1e-6)  # avoid divide-by-zero
    return cl / cd

def objective_to_minimize(x):
    return -predict_L_over_D(x)[0]  # negative for maximization

# --- Global optimization with Differential Evolution ---
print("\nRunning global optimization (Differential Evolution)...")
result_de = differential_evolution(
    objective_to_minimize,
    bounds=bounds,
    strategy="best1bin",
    popsize=15,
    maxiter=200,
    tol=1e-6,
    seed=0,
    disp=True
)

x_de = result_de.x
ld_de = predict_L_over_D(x_de)[0]
print("\nBest from Differential Evolution:")
print(f"  L/D = {ld_de:.6f}")
print("  Parameters:", x_de)

# --- Local refinement with SLSQP ---
print("\nRefining with local optimization (SLSQP)...")
result_local = minimize(
    objective_to_minimize,
    x0=x_de,
    method="SLSQP",
    bounds=bounds,
    options={"ftol": 1e-9, "maxiter": 500}
)

x_opt = result_local.x
ld_opt = predict_L_over_D(x_opt)[0]
print("\nOptimized Results:")
print(f"  Refined L/D = {ld_opt:.6f}")
print("  Refined parameters:", x_opt)

# --- Compare to best in training data ---
L_over_D_train = Y[:, 0] / Y[:, 1]  # cl/cd from your training data
best_train_idx = np.argmax(L_over_D_train)
print(f"\nBest training case L/D = {L_over_D_train[best_train_idx]:.6f} (case {best_train_idx})")
 