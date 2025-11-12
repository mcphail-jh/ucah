import numpy as np
from matplotlib import pyplot as plt

from KrigOpt import *
from kriging_2 import GenerateSM

# Reading data and developing surrogate model
data_path = "tests/optimization_tests/1d_test/data.csv"
param_num = 1
objective_name = "obj_func"
output_path = "tests/optimization_tests/1d_test/sm.pkl"
GenerateSM(data_path, param_num, objective_name, output_path)

# Setting up optimizer
opt = KrigOpt(ObjFuncSM="tests/optimization_tests/1d_test/sm.pkl", _debug=False)

print(eval_SM_value(opt.ObjFuncSM, np.array([[1], [2], [3], [4], [5], [6]])))
print(eval_SM_Jacobian(opt.ObjFuncSM, np.array([[5]])))
print(eval_SM_Jacobian(opt.ObjFuncSM, np.array([5])))


x = np.linspace(0, 7, 100)
y = eval_SM_value(opt.ObjFuncSM, x.reshape([100, 1]))
J = np.zeros(x.shape)
H = np.zeros(x.shape)

for i in range(0, 100):
    J[i] = eval_SM_Jacobian(opt.ObjFuncSM, np.array(x[i]).reshape([1, 1]))
    H[i] = eval_SM_Hessian(opt.ObjFuncSM, np.array(x[i]).reshape([1, 1]))

plt.plot(x, y, label="Interpolated Values")
plt.plot(x, J, label="Interpolated First Derivative")
plt.plot(x, H, label="Interpolated Second Derivative")
plt.scatter([1, 2, 3, 4, 5, 6], [3, 2, 1, 1, 2, 3])
plt.legend()
plt.show()
