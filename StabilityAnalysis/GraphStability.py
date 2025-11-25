
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


def eval_pitching_moment(X, d):
    Lift = KrigOpt(ObjFuncSM="StabilityAnalysis/Lift.pkl")
    Pitch = KrigOpt(ObjFuncSM="StabilityAnalysis/Pitch.pkl")
    dLda = Lift.ObjFuncSM.predict_derivatives(X, 1)
    dMda = Lift.ObjFuncSM.predict_derivatives(X, 1)
    return Pitch.ObjFuncSM.predict_values(X)  - d * Lift.ObjFuncSM.predict_values(X)

def eval_rolling_moment(X, d):
    Roll = KrigOpt(ObjFuncSM="StabilityAnalysis/Roll.pkl")
    return Roll.ObjFuncSM.predict_values(X)

def eval_yawing_moment(X, d):
    Yaw = KrigOpt(ObjFuncSM="StabilityAnalysis/Yaw.pkl")
    return Yaw.ObjFuncSM.predict_values(X)

def plotPitchMoment(d, M = 5, b = 0, num = 100, color=None):
    X = evalPathPoints(np.array([M, 0, b]), np.array([0, 1, 0]), [-10, 10], num)
    Y = eval_pitching_moment(X, d)
    plt.plot(X[:, 1], Y, label=f"d: {d}, M: {M}, b: {b}", c=color)

def plotYawingMoment(d, M=5, a=0, num=100, color=None):
    X = evalPathPoints(np.array([M, a, 0]), np.array([0, 0, 1]), [-10, 10], num)
    Y = eval_yawing_moment(X, d)
    plt.plot(X[:, 2], Y, label=f"d: {d}, M: {M}, a: {a}", c=color)

def plotRollingMoment(d, M=5, a=0, num=100, color=None):
    X = evalPathPoints(np.array([M, a, 0]), np.array([0, 0, 1]), [-10, 10], num)
    Y = eval_rolling_moment(X, d)
    plt.plot(X[:, 2], Y, label=f"d: {d}, M: {M}, a: {a}", c=color)


# Longitudinal Stability
plt.plot([-10, 10], [0, 0], c="lightgray")

X1 = np.array([5])
X2 = np.array([8])
C1 = np.array([252/255, 186/255, 3/255])
C2 = np.array([66/255, 135/255, 245/255])
num = 7

X = np.linspace(X1, X2, num)
C = np.linspace(C1, C2, num)
for i in range(0, num):
    plotPitchMoment(0.9, float(X[i, 0]), 0, color=C[i, :])

plt.legend()
plt.xlabel("Angle of Attack, [deg]")
plt.ylabel("Pitching Moment, [Nm]")
plt.savefig("StabilityAnalysis/Plots/PitchMomentsVsAOA")
plt.clf()

# Yaw Stability
plt.plot([-10, 10], [0, 0], c="lightgray")

X1 = np.array([5])
X2 = np.array([8])
C1 = np.array([252/255, 186/255, 3/255])
C2 = np.array([66/255, 135/255, 245/255])
num = 7

X = np.linspace(X1, X2, num)
C = np.linspace(C1, C2, num)
for i in range(0, num):
    plotYawingMoment(0.5,  float(X[i, 0]), 0, color=C[i, :])

plt.legend()
plt.xlabel("Sideslip Angle, [deg]")
plt.ylabel("Yawing Moment, [Nm]")
plt.savefig("StabilityAnalysis/Plots/YawMomentsVsAOA")
plt.clf()

# Roll Stability
plt.plot([-10, 10], [0, 0], c="lightgray")

X1 = np.array([5])
X2 = np.array([8])
C1 = np.array([252/255, 186/255, 3/255])
C2 = np.array([66/255, 135/255, 245/255])
num = 7

X = np.linspace(X1, X2, num)
C = np.linspace(C1, C2, num)
for i in range(0, num):
    plotRollingMoment(0.5,  float(X[i, 0]), 0, color=C[i, :])

plt.legend()
plt.xlabel("Sideslip Angle, [deg]")
plt.ylabel("Rolling Moment, [Nm]")
plt.savefig("StabilityAnalysis/Plots/RollMomentsVsAOA")
plt.clf()



# x0 = np.array([8, 0, 0])
# num_points = 100
#
# # Plotting Lift Force vs AoA
# bounds = [-10, 10]
# Lift.plotPath(x0, np.array([0, 1, 0]), bounds, num_points, var=False, label="Lift Force")
# plt.plot(bounds, [0, 0])
# plt.xlabel("Angle of Attack, [deg]")
# plt.ylabel("Lift Force [kNm]")
# plt.show()
#
# # Plotting Pitching Moment vs AoA
# bounds = [-10, 10]
# Pitch.plotPath(x0, np.array([0, 1, 0]), bounds, num_points, var=False, label="Pitching Moment")
# plt.plot(bounds, [0, 0])
# plt.xlabel("Angle of Attack, [deg]")
# plt.ylabel("Pitching Moment, [kNm]")
# plt.show()
#
# # Plotting Yawing Moment vs Sideslip Angle
# Yaw.plotPath(x0, np.array([0, 0, 1]), bounds, num_points, var=False, label="Yawing Moment")
# plt.plot(bounds, [0, 0])
# plt.xlabel("Sideslip angle, [deg]")
# plt.ylabel("Yawing Moment, [kNm]")
# plt.show()
#
# # Plotting Rolling Moment vs Sideslip Angle
# Roll.plotPath(x0, np.array([0, 0, 1]), bounds, num_points, var=False, label="Rolling Moment")
# plt.plot(bounds, [0, 0])
# plt.xlabel("Sideslip angle, [deg]")
# plt.ylabel("Rolling Moment, [kNm]")
# plt.show()
