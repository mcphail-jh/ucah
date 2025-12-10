
class kriging_obj:
    def __init__(self, csv_file,aero_cols, n_params):
        self.aero_cols = aero_cols
        self.n_params = n_params
        self.csv_file = csv_file
    def get_xy(self):
        import pandas as pd
        import numpy as np
        import pickle
        from smt.surrogate_models import KRG

        # --- Input/Output File Names ---
        models_out = {
            "cl": "krg_cl.pkl",
            "cd": "krg_cd.pkl",
            "cm": "krg_cm.pkl",
        }
        data_csv = self.csv_file
        self.models_out = models_out
        # --- Load CSV ---
        df = pd.read_csv(data_csv, header=0)
        print("Full data shape (with case name column):", df.shape)

        # --- Identify columns ---
        n_params = self.n_params
        param_cols = df.columns[1:1 + n_params]  # skip case name column
        aero_cols = self.aero_cols

        # --- Basic checks ---
        if not all(c in df.columns for c in aero_cols):
            raise ValueError(f"CSV must contain aerodynamic columns: {aero_cols}")

        # --- Split data ---
        X = df[param_cols].to_numpy(dtype=float)  # shape (n_cases, 15)
        Y = df[aero_cols].to_numpy(dtype=float)   # shape (n_cases, 3)

        print("Processed X shape (n_samples, n_params):", X.shape)
        print("Processed Y shape (n_samples, n_outputs):", Y.shape)

        self.X = X
        self.Y = Y
        return X, Y
    
    def run_kriging(self):
        from smt.surrogate_models import KRG
        import pickle
        X,Y = self.get_xy()

        # --- Train Kriging models ---
        krg_options = dict(theta0=[1e-2]*X.shape[1], hyper_opt="Cobyla")

        trained_models = {}
        for i, col in enumerate(self.aero_cols):
            y_vec = Y[:, i]
            print(f"\nTraining KRG for {col} ...")
            sm = KRG(**krg_options)
            sm.set_training_values(X, y_vec)
            sm.train()
            trained_models[col] = sm

            # Save model
            with open(self.models_out[col], "wb") as f:
                pickle.dump(sm, f)
            print(f"Saved {col} model to {self.models_out[col]}")