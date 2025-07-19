import pandas as pd
import matplotlib.pylab as plt


data2 = {
    'num_robots': [20 ,25, 30, 35, 40, 45, 50, 55],
    'tiempo_espera': [0.37, 0.463, 0.556, 0.648, 0.741, 0.833, 0.926, 1.019],#[137, 188, 313, 497, 681, 1574],
    'efectividad': [73.75,71.28,70.4,67.371,66.1,59.489,62.7,53.073]
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
plt.title('Relación entre número de robots, densidad y tiempo efectivo relativo')
plt.show()


# Datos de la tabla (9x6)
data3 = {
    'num_robots': [25, 30, 35, 40, 46, 50],
    'tiempo_espera': [5.2,6.86,8.37,9.3,17.78,17.8],#[130, 206, 293, 372, 818, 884],
    'efectividad': [0.464, 0.524344569, 0.637450199, 0.704, 0.70612245, 0.725868726]
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
plt.title('Relación entre número de robots, tiempo de espera y efectividad (9x6)')
plt.show()
