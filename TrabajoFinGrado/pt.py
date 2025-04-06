from mealpy import FloatVar, GA
import numpy as np

def objective_func(solution):
    return np.sum(solution**2)

problem_dict = {
    "obj_func": objective_func,
    "bounds": FloatVar(lb=[-100, ] * 30, ub=[100, ] * 30,),
    "minmax": "min",
}

optimizer = GA.BaseGA(epoch=100, pop_size=50, pc=0.85, pm=0.1)
optimizer.solve(problem_dict)

print(optimizer.g_best.solution)
print(optimizer.g_best.target.fitness)








asd
import mealpy
from funAuxTFG import cargar_informacion

data = cargar_informacion()
print(data)
datosTiempo = []