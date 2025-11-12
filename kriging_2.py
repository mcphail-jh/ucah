import pandas as pd
import numpy as np
import pickle
from smt.surrogate_models import KRG

def GenerateSM(
        data_path : str,
        param_num : int,
        objective_name : str,
        output_path : str = None
):
    # --- Load CSV ---
    data_file = pd.read_csv(data_path, header=0)
    print(f"Full data shape (with case name column): {data_file.shape}")

    # --- Identify Columns ---
    param_cols = data_file.columns[1:1 + param_num]

    # --- Basic Checks ---
    if not (objective_name in data_file.columns):
        raise ValueError(f"CSV must contain column labeled: {objective_name}")

    # --- Split Data ---
    X = data_file[param_cols].to_numpy(dtype=float)
    Y = data_file[objective_name].to_numpy(dtype=float)

    print(f"Processed X shape (n_samples, n_params): {X.shape}")
    print(f"Processed Y shape (n_samples, n_params): {Y.shape}")

    # --- Train Surrogate Model ---
    krg_options = dict(theta0=[1e-6]*X.shape[1], hyper_opt="Cobyla")
    print(f"\nTraining KRG ...")
    sm = KRG(**krg_options)
    sm.set_training_values(X, Y)
    sm.train()
    if output_path is not None:
        with open(output_path, "wb") as f:
            pickle.dump(sm, f)
        print(f"Saved outputs to {output_path}.")

    return sm

