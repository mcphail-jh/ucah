from KrigOpt import *

opt = KrigOpt(ObjFuncSM="tests/optimization_tests/1d_test/krg_OF.pkl", _debug=False)

print(eval_SM_value(opt.ObjFuncSM, np.array([[1], [2], [3], [4], [5], [6]])))