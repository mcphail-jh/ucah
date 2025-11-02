import pickle
import matplotlib.pyplot as plt
import numpy as np

cd_path = "krg_OF.pkl"
with open(cd_path, 'rb') as file:
    krg_sm = pickle.load(file)

# print(type(krg_sm))
# print(krg_sm.optimal_par["gamma"])
# print(krg_sm.y_mean)
# print(krg_sm.y_std)

print(krg_sm.training_points[None][0][0])
# print(krg_sm.optimal_par["gamma"])
# print(krg_sm.optimal_par["beta"])
# print(krg_sm.corr.theta)
# print(krg_sm.y_mean)
# print(krg_sm.y_std)
# print(krg_sm.X_offset)
# print(krg_sm.X_scale)

num = 100;
x = np.zeros([num, 1])
x[:, 0] = np.linspace(-5, 20, num)
y = krg_sm.predict_values(x)

_, axs = plt.subplots(1)
axs.plot(x[:, 0],y)
axs.scatter([1, 2, 3, 4, 5, 6], [3, 2, 1, 1, 2, 3])
plt.show()