import numpy as np
import pandas as pd
import pickle
from kriging2pkl import kriging_obj

data_csv = "krig_file.csv"  # single CSV with all params + cl, cd, cm

krig = kriging_obj(data_csv,aero_cols=["cl", "cd", "cm"], n_params=3)
krig.get_xy()
krig.run_kriging()


models_out = {
            "cl": "krg_cl.pkl",
            "cd": "krg_cd.pkl",
            "cm": "krg_cm.pkl",
        }

with open(models_out["cl"], "rb") as f:
    krg_cl = pickle.load(f)
with open(models_out["cd"], "rb") as f:
    krg_cd = pickle.load(f)
with open(models_out["cm"], "rb") as f:
    krg_cm = pickle.load(f)
thing = krg_cd.predict_values(np.atleast_2d(np.array([20, 40, 20])))[0][0]
print(f'value is: {thing}') # warm up model to avoid threading issues later