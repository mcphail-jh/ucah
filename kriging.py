import pandas as pd
import numpy as np
import pickle
from smt.surrogate_models import KRG

# ---Names Input Files and Output Files----
X_csv = "params.csv"        # first column = case name, top-left cell blank, top row contains 15 param names
Y_csv = "aero_outputs.csv"  # top row: cl,cd,cm ; subsequent rows: 50 rows with matching order to params.csv
models_out = { "cl": "krg_cl.pkl", "cd": "krg_cd.pkl", "cm": "krg_cm.pkl" } #files for kriging model output 

# --- Load CSVs with pandas ---
X_df = pd.read_csv(X_csv, header=0)
Y_df = pd.read_csv(Y_csv, header=0)

# Inspect shapes and output their # of rows and columns 
print("X shape (with name column):", X_df.shape)
print("Y shape:", Y_df.shape)

# --- Drop first column (case names) of input parameters ---
X = X_df.iloc[:, 1:].to_numpy(dtype=float)   # shape: (50, 15)
print("Processed X shape (n_samples, n_params):", X.shape)

# --- Preprocess Y: ensure we have exactly 3 columns named cl,cd,cm (case order matches X) ---
expected_cols = ["cl", "cd", "cm"]
if not all(c in Y_df.columns for c in expected_cols):
    raise ValueError(f"Y CSV must contain columns: {expected_cols}. Found: {list(Y_df.columns)}")
Y = Y_df[expected_cols].to_numpy(dtype=float)  # shape: (50, 3)
print("Processed Y shape (n_samples, n_outputs):", Y.shape)

# --- Basic check: same number of rows ---
if X.shape[0] != Y.shape[0]:
    raise ValueError("X and Y must have the same number of rows (cases).")

# --- KRIGING TRAINING (One per output variable ) ---
# Recommended: set hyper_opt to 'Cobyla' or 'BFGS' or leave default; theta0 can help converge.
krg_options = dict(theta0=[1e-2]*X.shape[1], hyper_opt="Cobyla")  # example options

trained_models = {}
for i, col in enumerate(expected_cols): #one KRG for each cl,cd,cm 
    y_vec = Y[:, i]   # 1-D vector for SMT
    print(f"\nTraining KRG for {col} ...")
    sm = KRG(**krg_options)   # you can add eval_noise=True if your outputs are noisy
    sm.set_training_values(X, y_vec)
    sm.train()
    trained_models[col] = sm

    # Save model to disk (pickle)
    with open(models_out[col], "wb") as f:
        pickle.dump(sm, f)
    print(f"Saved {col} model to {models_out[col]}")

# --- Example: predicting with the trained models ---
# Suppose you have a new parameter set(s) X_new as numpy array shape (n_new, 15):
# For demonstration use the first two training points:
# X_new = X[:2, :]

# predictions = {}
# variances = {}
# for col, sm in trained_models.items():
#     y_pred = sm.predict_values(X_new)      # shape: (n_new, ) or (n_new,1)
#     y_var  = sm.predict_variances(X_new)   # predictive variances
#     predictions[col] = np.ravel(y_pred)
#     variances[col]   = np.ravel(y_var)
#     print(f"\nPredictions for {col}: {predictions[col]}")
#     print(f"Variances  for {col}: {variances[col]}")

# # --- Optional: save predictions/variances as CSV ---
# out_df = pd.DataFrame(predictions)
# out_var_df = pd.DataFrame(variances)
# out_df.to_csv("predictions_example.csv", index=False)
# out_var_df.to_csv("pred_vars_example.csv", index=False)
# print("\nDone.")
