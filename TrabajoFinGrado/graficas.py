import pandas as pd
import matplotlib.pylab as plt


data2 = {
    'num_robots': [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90],
    'tiempo_espera': [0.278, 0.313, 0.347, 0.382, 0.417, 0.451, 0.486, 0.521, 0.556, 0.59, 0.625],#[0.37037037, 0.462962963, 0.555555556, 0.648148148, 0.740740741, 0.833333333, 0.925925926, 1.037037037], #[0.37, 0.463, 0.556, 0.648, 0.741, 0.833, 0.926, 1.019],#[137, 188, 313, 497, 681, 1574],
    'efectividad': [80.55, 78.911, 75.3, 76.309, 73.033, 69.262, 65.257, 60.653, 59.263, 56.647, 53.378]#[75.1, 74.04, 70.66666667, 70.97142857, 68.025, 70.26666667, 59.86, 34.92857143] #[73.75,71.28,70.4,67.371,66.1,59.489,62.7,53.073]
}

df2 = pd.DataFrame(data2)

fig, ax1 = plt.subplots(figsize=(8,5))
ax1.set_xlabel('Número de robots')
ax1.set_ylabel('Densidad (tanto por uno)', color='tab:blue')
ax1.plot(df2['num_robots'], df2['tiempo_espera'], marker='o', color='tab:blue', label='Tiempo de espera relativo')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Tiempo efectivo relativo (steps)', color='tab:red')
ax2.plot(df2['num_robots'], df2['efectividad'], marker='s', color='tab:red', label='Efectividad')
ax2.tick_params(axis='y', labelcolor='tab:red')
figsize=(14,9)

fig.tight_layout()
plt.title('Relación entre número de robots, densidad y tiempo efectivo relativo (12x12)')
plt.show()


# Datos de la tabla (9x6)
data3 = {
    'num_robots': [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90],
    'tiempo_espera': [7.575, 8.356, 11.44, 11.927, 14.317, 18.462, 23.257, 30.627, 31.925, 35.447, 39.489],#[4.4, 5.48, 6.266666667, 9.142857143, 11.3, 12.28888889, 23.8, 31.48214286],# [5.2,6.86,8.37,9.3,17.78,17.8],#[130, 206, 293, 372, 818, 884],
    'efectividad': [0.505, 0.49, 0.542, 0.619, 0.609, 0.581, 0.659, 0.637, 0.642, 0.645, 0.637] #[0.454545455, 0.543650794, 0.616935484, 0.749003984, 0.78313253, 0.738095238, 0.768939394, 0.790322581] #[0.464, 0.524344569, 0.637450199, 0.704, 0.70612245, 0.725868726]
}

df3 = pd.DataFrame(data3)

fig, ax1 = plt.subplots(figsize=(8,5))
ax1.set_xlabel('Número de robots')
ax1.set_ylabel('Tiempo de espera', color='tab:blue')
ax1.plot(df3['num_robots'], df3['tiempo_espera'], marker='o', color='tab:blue', label='Tiempo de espera')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Efectividad', color='tab:red')
ax2.plot(df3['num_robots'], df3['efectividad'], marker='s', color='tab:red', label='Efectividad')
ax2.tick_params(axis='y', labelcolor='tab:red')

fig.tight_layout()
plt.title('Relación entre número de robots, tiempo de espera y efectividad (12x12)')
plt.show()
