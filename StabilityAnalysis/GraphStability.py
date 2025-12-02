from StabilityAnalyzer import StabilityAnalyzer


# Controls:
READ_PKLs = False

# --- Read in CSV Data ---
if READ_PKLs:
    from kriging_2 import GenerateSM
    GenerateSM("AeroData.csv", 3, "lift_force", "pickles/Lift.pkl")
    GenerateSM("AeroData.csv", 3, "drag_force", "pickles/Drag.pkl")
    GenerateSM("AeroData.csv", 3, "sideforce", "pickles/Sideforce.pkl")
    GenerateSM("AeroData.csv", 3, "moment", "pickles/Pitch.pkl")
    GenerateSM("AeroData.csv", 3, "yaw_mom", "pickles/Yaw.pkl")
    GenerateSM("AeroData.csv", 3, "roll_mom", "pickles/Roll.pkl")

StabAnlzr = StabilityAnalyzer(CoG_location=[0.5, 0.03])
StabAnlzr.plotStaticStability(5)