
# =======================================================================
# === OPTIMIZATION OF L/D USING TRAINED KRG MODELS ======================
# =======================================================================
import numpy as np
import pandas as pd
import pickle
from scipy.optimize import differential_evolution, minimize, NonlinearConstraint
from kriging2pkl import kriging_obj

lift_val = 3000



data_csv = "data_table.csv"  # single CSV with all params + cl, cd, cm

krig = kriging_obj(data_csv,aero_cols=["cl", "cd", "cm"], n_params=2)
X, Y = krig.get_xy()

# --- Load the trained cl and cd Kriging models ---
with open(krig.models_out["cl"], "rb") as f:
    krg_cl = pickle.load(f)
with open(krig.models_out["cd"], "rb") as f:
    krg_cd = pickle.load(f)
with open(krig.models_out["cm"], "rb") as f:
    krg_cm = pickle.load(f)
thing = krg_cd.predict_values(np.atleast_2d(np.array([20, 40])))  # warm up model to avoid threading issues later


def moment_calc(x):
    x = np.atleast_2d(x)
    cm_pred = krg_cm.predict_values(x)[0]
    return cm_pred

def lift_calc(x):
    x = np.atleast_2d(x)
    cl_pred = krg_cl.predict_values(x)[0]
    return cl_pred

def drag_with_mo(x):
    x = np.atleast_2d(x)
    cd_pred = krg_cd.predict_values(x)[0]
    cd_pred = cd_pred*cd_pred
    return cd_pred  

def objective_to_minimize(x):
    return -drag_with_mo(x)

thing = drag_with_mo(np.array([46.6,24.8]))
print(f"Test drag at (46,24.8): {thing}")

# 4. Define constraints
mom_con = NonlinearConstraint(moment_calc, -np.inf, 0)
lift_con = NonlinearConstraint(lift_calc, lift_val, np.inf)

cm = moment_calc(np.array([20,40]))

bounds = [(np.min(X[:, j]), np.max(X[:, j])) for j in range(X.shape[1])]

# 5. Run differential_evolution
result = differential_evolution(
    drag_with_mo, 
    bounds=bounds, 
    constraints=(mom_con,lift_con),
    strategy="best1bin",
    popsize=15,
    maxiter=200,
    tol=1e-6,
    seed=0,
    disp=False  # Constraints must be passed as a sequence (tuple or list))
)

print(f"Optimal solution (x1, x2): {result.x}")
print(f"Minimum value: {result.fun}")
print(f"Moment Value: {moment_calc(result.x)}")
print(f"Lift Value: {lift_calc(result.x)}")
print(f"Drag Value: {drag_with_mo(result.x)}")

print("\nRefining with local optimization (SLSQP)...")
result_local = minimize(
    objective_to_minimize,
    x0=result.x,
    method="SLSQP",
    bounds=bounds,
    constraints=(mom_con,lift_con),
    options={"ftol": 1e-9, "maxiter": 500}
)

x_opt = result_local.x
ld_opt = -objective_to_minimize(x_opt)
print(f"Optimal solution (x1, x2): {x_opt}")
print(f"First solution: {result.x}")    
print(f"Minimum value: {ld_opt}")