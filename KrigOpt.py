from smt.surrogate_models import KRG
from smt.kernels import PowExp
import numpy as np
import pickle

def importPKL(path, type_return):
    with open(path, 'rb') as file:
        to_return = pickle.load(file)

    if type(to_return) != type_return:
        raise ValueError(f"Cannot open {path} as type {type_return}")

    return to_return

def SM_transform(sm: KRG, x: np.array) -> np.array:
    # Transforms the input vector x into the space used by the surrogate model.
    return (x - sm.X_offset) / sm.X_scale

def eval_SM_value(sm: KRG, x: np.array) -> np.array:
    b = sm.optimal_par["beta"]
    g = sm.optimal_par["gamma"]
    t = sm.corr.theta

    xt : np.array = sm.training_points[None][0][0] # training parameter values.
    m, n = xt.shape
    X = SM_transform(sm, xt)

    num_x, nx = x.shape

    if nx != n:
        raise ValueError("")

    y = np.zeros([num_x, 1])

    for i in range(0, num_x): # Should be able to get rid of this for loop using a 3d array.
        dx = np.repeat(SM_transform(sm, x[i,:]), m).reshape([m, n])
        R = np.exp(-t * np.linalg.norm(dx - X, axis=1)**2).reshape([m, 1])  # TODO: make this more efficient
        y_s = sum(g * R)
        y[i] = sm.y_mean + sm.y_std * (b + y_s)
    return y

def eval_SM_Jacobian(sm, x):
    # TODO: implement this method
    # J = [g dRdx] + [1 - I]*R <- from product rule.
    #    dRdx is an [m x n] Jacobian matrix of the autocorrelation function.
    #    R is [m x n] autocorrelation matrix
    return

class KrigOpt:
    _debug : bool # if true, prints extra information during operation.
    ObjFuncSM : KRG # Kriging surrogate model of the objective function over the design space.

    def __init__(self, ObjFuncSM : [KRG, str], _debug : bool = False):
        self._debug = _debug

        if type(ObjFuncSM) == str:
            ObjFuncSM = importPKL(ObjFuncSM, KRG)
        self.setSM(ObjFuncSM)
        return

    def setSM(self, ObjFuncSM: KRG):
        if type(ObjFuncSM.corr) != PowExp:
            raise ValueError("Surrogate model not trained with correct correlation function. Please leave a default 'squar_exp'.")
        if ObjFuncSM.options["pow_exp_power"] != 2.0:
            raise ValueError("Surrogate model not trained with correct exponential power. Please leave as default '2.0'.")
        self.ObjFuncSM = ObjFuncSM
        if self._debug: print("Successfully set surrogate model.")
