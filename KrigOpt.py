from smt.surrogate_models import KRG
from smt.kernels import PowExp

import numpy as np
import pickle
from matplotlib import pyplot as plt


def importPKL(path, type_return):
    with open(path, 'rb') as file:
        to_return = pickle.load(file)

    if type(to_return) != type_return:
        raise ValueError(f"Cannot open {path} as type {type_return}")

    return to_return

def SM_transform(sm: KRG, x: np.array) -> np.array:
    # Transforms the input vector x into the space used by the surrogate model.
    return (x - sm.X_offset) / sm.X_scale

def eval_SM_Jacobian(sm : KRG, x: np.array) -> np.array:
    b = sm.optimal_par["beta"]
    g = sm.optimal_par["gamma"]
    t = sm.corr.theta

    xt : np.array = sm.training_points[None][0][0] # training parameter values.
    num_points, num_dims = xt.shape
    X = SM_transform(sm, xt)

    dx = SM_transform(sm, x)
    R = np.exp(-t * np.linalg.norm(dx - X, axis=1) ** 2).reshape([num_points, 1]) # TODO: make this more efficient
    J = np.zeros([num_dims, 1])
    for k in range(0, num_dims):
        out = 0
        for i in range(0, num_points):
            out += - g[i] * t * (dx[k] - X[i, k]) * R[i]
        J[k] = out
    return 2 * sm.y_std * J / sm.X_scale

def eval_SM_Hessian(sm : KRG, x: np.array) -> np.array:
    b = sm.optimal_par["beta"]
    g = sm.optimal_par["gamma"]
    t = sm.corr.theta

    xt : np.array = sm.training_points[None][0][0] # training parameter values.
    num_points, num_dims = xt.shape
    X = SM_transform(sm, xt)

    dx = SM_transform(sm, x)
    R = np.exp(-t * np.linalg.norm(dx - X, axis=1) ** 2).reshape([num_points, 1]) # TODO: make this more efficient
    H = np.zeros([num_dims, num_dims])
    for i in range(0, num_dims):
        for j in range(0, num_dims):
            out = 0
            if i == j:
                for k in range(0, num_points):
                    out += g[k] * t * ((dx[i] - X[k, i])**2 - 1) * R[k]
            else:
                for k in range(0, num_points):
                    out += 4 * g[k] * (t**2) * (dx[i] - X[k, i]) * (dx[j] - X[k, j]) * R[k]
            H[i, j] = out
    return sm.y_std * H / sm.X_scale

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
        print(np.sum(t * (dx - X)**2, axis=1))
        R = np.exp(-np.sum(t * (dx - X)**2, axis=1)).reshape([m, 1])  # TODO: make this more efficient
        y_s = sum(g * R)
        y[i] = sm.y_mean + sm.y_std * (b + y_s)
    return y


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

    def evalPathValues(self, x0, dir, bounds, n=100):
        x_dims = x0.size
        x = np.linspace(bounds[0], bounds[1], n).reshape([n, 1]) * np.repeat(dir.reshape([1, x_dims]), n, axis=0) + np.repeat(x0.reshape([1, x_dims]), n, axis=0)
        y = self.ObjFuncSM.predict_values(x)
        return y.reshape(-1)

    def evalPathVariances(self, x0, dir, bounds, n=100):
        x_dims = x0.size
        x = np.linspace(bounds[0], bounds[1], n).reshape([n, 1]) * np.repeat(dir.reshape([1, x_dims]), n, axis=0) + np.repeat(x0.reshape([1, x_dims]), n, axis=0)
        u = self.ObjFuncSM.predict_variances(x)
        return u.reshape(-1)

    def plotPath(self, x0, dir, bounds, n=100, color=None, label=None, var:bool=True):

        x = np.linspace(bounds[0], bounds[1], n) + np.dot(x0, dir)
        y = self.evalPathValues(x0, dir, bounds, n)
        line, = plt.plot(x, y, color=color, label=label)

        if var:
            u = self.evalPathVariances(x0, dir, bounds, n)
            plt.fill_between(x, y + 2 * u, y - 2 * u, color=line.get_color(), alpha=0.5, linewidth=0)