import numpy as np
import pickle
from smt.surrogate_models import KRG
from matplotlib import pyplot as plt

_DIR_PATH = "StabilityAnalysis/"
_DEFAULT_KRG_VALS = {
    "Lift": "pickles/Lift.pkl",
    "Drag": "pickles/Drag.pkl",
    "Side": "pickles/Sideforce.pkl",
    "MomP": "pickles/Pitch.pkl",
    "MomY": "pickles/Yaw.pkl",
    "MomR": "pickles/Roll.pkl",
}

def _readKRG(KRG_val: KRG | str, dir_path="") -> KRG:
    if type(KRG_val) == str:
        with open(dir_path+KRG_val, "rb") as f:
            KRG_val = pickle.load(f)
    return KRG_val

def LDStoXYZ(forces):
    num_rows, num_cols = forces.shape

    transform = np.array([
        [0, 0, -1],
        [-1, 0, 0],
        [0,  1, 0]
    ])

    for i in range(0, num_rows):
        forces[i, :] = (forces[i, :].reshape(1, 3)) @ transform
    return forces

def PYWtoXYZ(moments):
    num_rows, num_cols = moments.shape

    transform = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0]
    ])

    for i in range(0, num_rows):
        moments[i, :] = (moments[i, :].reshape(1, 3)) @ transform
    return moments

def _checkInputs(X: np.array):
    assert (X.ndim <= 2), f"Input Array is {X.ndim}-dimensional. (expected 2)"
    if X.ndim == 1:
        X = X.reshape([1, X.size])
    num_rows, num_cols = X.shape
    assert (num_cols == 3), f"Input Array has {num_cols} inputs. (expected 3)"

class StabilityAnalyzer:

    CoG: np.array  # CoG Coordinates in the body frame.
    Origin: np.array  = np.array([[0], [0], [0]]) # Coordinates of points moments are recorded about.

    # KRG Models
    Lift: KRG
    Drag: KRG
    Side: KRG
    MomP: KRG
    MomY: KRG
    MomZ: KRG

    def __init__(self, CoG_location=None, KRGs : {str: KRG | str} = None):
        """

        :param CoG_location: CoG coordinates in the body frame [x, z]
        :param KRGs: Dict (Lift, Drag, Side, MomP, MomY, MomR) -> (KRG | path.pkl)
        """
        # Set default CoG location
        if CoG_location is None:
            CoG_location = [0.5, 0.003]

        # Set default KRGs values
        if KRGs is None:
            KRGs = {}
        for key in ("Lift", "Drag", "Side", "MomP", "MomY", "MomR"):
            if KRGs.get(key) is None:
                KRGs[key] = _DEFAULT_KRG_VALS[key]

        # Set init values Location
        self.setCoG(CoG_location)
        self.setKRGs(KRGs, False)

    def setCoG(self, CoG: list):
        """
        Sets the Analyzer's CoG Position.
        :param CoG: CoG coordinates in the body frame [x, z]
        """
        # Creates array from input list.
        if type(CoG) != np.array:
            CoG = np.array(CoG)
        CoG = CoG.reshape(-1)

        # Checking inputted CoG Position.
        assert(CoG.size == 2), f"CoG position is of size {CoG.size}"
        assert(0 <= CoG[0] <= 1), f"CoG x position {CoG[0]} is outside the valid range [0, 1]"
        # assert(-0.01 <= CoG[1] <= 0.01), f"CoG x position {CoG[1]} is outside the valid range [0, 0.01]"

        # Adds a zero y coordinate.
        CoG = np.insert(CoG, 1, 0)
        self.CoG = CoG.reshape([3, 1])

    def setKRGs(self, KRGs: {str: KRG | str}, addDirPath: bool = False):
        if not addDirPath:
            dir_path = ""
        else:
            dir_path = _DIR_PATH
        self.Lift = _readKRG(KRGs["Lift"], dir_path)
        self.Drag = _readKRG(KRGs["Drag"], dir_path)
        self.Side = _readKRG(KRGs["Side"], dir_path)
        self.MomP = _readKRG(KRGs["MomP"], dir_path)
        self.MomY = _readKRG(KRGs["MomY"], dir_path)
        self.MomR = _readKRG(KRGs["MomR"], dir_path)

    def _eval_forces(self, X: np.array, checkInput: bool = True) -> np.array:
        """
        Polls the KRGs to find the forces acting on the origin at inputs X.
        :param X: Mach, AoA, and Sideslip Angle pairs [[M1, A1, B1], ..., [Mn, An, Bn]]
        :return: Forces [[Lift1, Drag1, Side1], ..., [Liftn, Dragn, Siden]]
        """
        if checkInput:
            _checkInputs(X)
        lift = self.Lift.predict_values(X)
        drag = self.Drag.predict_values(X)
        side = self.Side.predict_values(X)
        forces = np.concatenate((lift, drag, side), axis=1)
        return forces

    def _eval_moments(self, X: np.array, checkInput: bool = True) -> np.array:
        """
        Polls the KRGs to find the forces acting on the origin at inputs X.
        :param X: Mach, AoA, and Sideslip Angle pairs [[M1, A1, B1], ..., [Mn, An, Bn]]
        :return: Forces [[Pitch1, Yaw1, Roll1], ..., [Pitchn, Yawn, Rolln]]
        """
        if checkInput:
            _checkInputs(X)
        momP = self.MomP.predict_values(X)
        momY = self.MomY.predict_values(X)
        momR = self.MomR.predict_values(X)
        moments = np.concatenate((momP, momY, momR), axis=1)
        return moments

    def evalReactions(self, X: np.array) -> np.array:
        _checkInputs(X)
        forces_LDS = self._eval_forces(X, False)
        forces = LDStoXYZ(forces_LDS)
        moments_PYR = self._eval_moments(X, False)
        moments = PYWtoXYZ(moments_PYR)

        r = (self.CoG - self.Origin).reshape(-1)
        num_rows, num_cols = X.shape
        reactions = np.zeros([num_rows, 6])
        for i in range(0, num_rows):
            force_i = forces[i, :].reshape(-1)
            moment_i = moments[i, :] - np.cross(r, force_i).reshape(-1)
            reactions[i, :] = np.concatenate((force_i, moment_i))
        return reactions

    def plotStaticStability(self, M):
        AlphaBounds = [-10, 10]
        BetaBounds = [-5, 5]
        num_points = 1000

        # Plotting Pitch Stability
        X_start = np.array([M, AlphaBounds[0], 0])
        X_end = np.array([M, AlphaBounds[1], 0])
        X = np.linspace(X_start, X_end, num_points, axis=0)
        reactions = self.evalReactions(X)
        momP = reactions[:, 4]
        plt.plot(X[:, 1], momP)
        plt.plot(AlphaBounds, [0, 0])
        plt.title("Pitching Moment vs Angle of Attack")
        plt.xlabel("Angle of attack, alpha [deg]")
        plt.ylabel("Pitching Moment, m [Nm]")
        plt.savefig("Plots/PitchStability.png")
        plt.clf()

        # Plotting Yaw and Roll Stability
        X_start = np.array([M, 0, BetaBounds[0]])
        X_end = np.array([M, 0, BetaBounds[1]])
        X = np.linspace(X_start, X_end, num_points, axis=0)
        reactions = self.evalReactions(X)
        momY = reactions[:, 5]
        momR = reactions[:, 3]
        plt.plot(X[:, 2], momY)
        plt.plot(BetaBounds, [0, 0])
        plt.title("Yawing Moment vs Sideslip Angle")
        plt.xlabel("Sideslip Angle, beta [deg]")
        plt.ylabel("Yawing Moment, n [Nm]")
        plt.savefig("Plots/YawStability.png")
        plt.clf()

        plt.plot(X[:, 2], momR)
        plt.plot(BetaBounds, [0, 0])
        plt.title("Rolling Moment vs Sideslip Angle")
        plt.xlabel("Sideslip Angle, beta [deg]")
        plt.ylabel("Rolling Moment, l [Nm]")
        plt.savefig("Plots/RollStability.png")
        plt.clf()




if __name__ == "__main__":
    test_analyzer = StabilityAnalyzer([0.5, -0.003])
    X = np.array([
        [1, 1, 1],
        [2, 2, 2]
    ])
    reactions = test_analyzer.evalReactions(X)
    print(reactions)