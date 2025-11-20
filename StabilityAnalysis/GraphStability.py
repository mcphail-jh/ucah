
import numpy as np
from matplotlib import pyplot as plt

from KrigOpt import *
from kriging_2 import GenerateSM

# Reading data and developing surrogate model
data_path = "StabilityAnalysis/Master.csv"
param_num = 3
GenerateSM(data_path, param_num, "lift_force", "StabilityAnalysis/Lift.pkl")
GenerateSM(data_path, param_num, "moment", "StabilityAnalysis/Pitch.pkl")
GenerateSM(data_path, param_num, "yaw_mom", "StabilityAnalysis/Yaw.pkl")
GenerateSM(data_path, param_num, "roll_mom", "StabilityAnalysis/Roll.pkl")

# Setting up optimizer
Lift = KrigOpt(ObjFuncSM="StabilityAnalysis/Lift.pkl")
Pitch = KrigOpt(ObjFuncSM="StabilityAnalysis/Pitch.pkl")
Yaw = KrigOpt(ObjFuncSM="StabilityAnalysis/Yaw.pkl")
Roll = KrigOpt(ObjFuncSM="StabilityAnalysis/Roll.pkl")

x0 = np.array([5, 0, 0])
num_points = 100

# Plotting Lift Force vs AoA
bounds = [-10, 10]
Lift.plotPath(x0, np.array([0, 1, 0]), bounds, num_points, var=False, label="Lift Force")
plt.plot(bounds, [0, 0])
plt.xlabel("Angle of Attack, [deg]")
plt.ylabel("Lift Force [kNm]")
plt.show()

# Plotting Pitching Moment vs AoA
bounds = [-10, 10]
Pitch.plotPath(x0, np.array([0, 1, 0]), bounds, num_points, var=False, label="Pitching Moment")
plt.plot(bounds, [0, 0])
plt.xlabel("Angle of Attack, [deg]")
plt.ylabel("Pitching Moment, [kNm]")
plt.show()

# Plotting Yawing Moment vs Sideslip Angle
Yaw.plotPath(x0, np.array([0, 0, 1]), bounds, num_points, var=False, label="Yawing Moment")
plt.plot(bounds, [0, 0])
plt.xlabel("Sideslip angle, [deg]")
plt.ylabel("Yawing Moment, [kNm]")
plt.show()

# Plotting Rolling Moment vs Sideslip Angle
Roll.plotPath(x0, np.array([0, 0, 1]), bounds, num_points, var=False, label="Rolling Moment")
plt.plot(bounds, [0, 0])
plt.xlabel("Sideslip angle, [deg]")
plt.ylabel("Rolling Moment, [kNm]")
plt.show()
