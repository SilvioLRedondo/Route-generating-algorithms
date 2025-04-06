import networkx as nx
import matplotlib.pyplot as plt
import funTFG
from funAuxTFG import guardar_informacion,cargar_informacion



if __name__ == "__main__":
    n, m, k, d = 3, 1, 3, 0  # Parámetros del almacén  
    num_robots = 1
    
    tsam = 0.1
    total_simulation_time = 5  # Tiempo total de simulación (en segundos)

    graph = funTFG.GraphGen(n, m, k, d)
    
    # Extracción de información para visualización (opcional)
    posEstante = {node: node.posicion for node in graph.nodes()}
    Estantes = {node: node.estante for node in graph.nodes() if hasattr(node, "estante")}
    pasillos = {
        (nodo1, nodo2): {
            "peso": data["objeto_arista"].peso,
            "tipo": data["objeto_arista"].tipo,
            "capacidad": data["objeto_arista"].capacidad,
            "longitud": data["objeto_arista"].longitud()
        }
        for nodo1, nodo2, data in graph.edges(data=True)
    }
    # print("Información de los nodos:", posEstante, "\n")
    # print("Estantes en los nodos:", Estantes, "\n")
    # print("Información de las aristas:", pasillos, "\n")

    robots = funTFG.create_robots(num_robots, graph)
    info_robots = {
        robot.id: {
            "posición": robot.position,
            "objetivo": robot.target,
            "distancia": robot.distance,
            "capacidad_carga": robot.capacidad_carga,
            "autonomía": robot.autonomia,
            "disponible": robot.disponible
        }
        for robot in robots
    }
    # print("Información sobre los robots:", info_robots)

    # Fase 1: Cálculo previo de la simulación continua
    
    simulation_data = funTFG.simulate_robots_continuous(graph, robots, total_simulation_time, dt=tsam, speed=1)
    print(simulation_data)
    
    # resultado = [valor for sublista in simulation_data for valor in sublista[0]]
    # print(resultado)
    
    
    # Fase 2: Reproducción/visualización de la simulación
    funTFG.playback_simulation(graph, simulation_data, dt=tsam)
    print(simulation_data)
    
    guardar_informacion(simulation_data)
    prueba = cargar_informacion()
    print(prueba)
    









#------------#
# import networkx as nx
# import matplotlib.pyplot as plt
# import funTFGdisc

# if __name__ == "__main__":
#     n, m, k, d = 8, 6, 48, 1  # Parámetros del almacén  

#     num_robots = 8           # Número de robots
#     steps = 180              # Pasos de la simulación

    
#     graph = funTFGdisc.GraphGen(n, m, k, d)
    
#     # Para visualización se pueden obtener las posiciones y la información de los estantes a partir de los objetos
#     posEstante = {node: node.posicion for node in graph.nodes()}
#     Estantes = {node: node.estante for node in graph.nodes() if hasattr(node, "estante")}
#     pasillos = {
#         (nodo1, nodo2): {
#         "peso": data["objeto_arista"].peso,
#         "tipo": data["objeto_arista"].tipo,
#         "capacidad": data["objeto_arista"].capacidad,
#         "longitud": data["objeto_arista"].longitud()
#     }
#     for nodo1, nodo2, data in graph.edges(data=True)
#     }
#     print("Información de los nodos:", posEstante,"\n")
#     print("Estantes en los nodos:", Estantes, "\n")
#     print("Información de las aristas:", pasillos,"\n")

#     robots = funTFGdisc.create_robots(num_robots, graph)
#     info_robots = {
#     robot.id: {
#         "posición": robot.position,
#         "objetivo": robot.target,
#         "distancia": robot.distance,
#         "capacidad_carga": robot.capacidad_carga,
#         "autonomía": robot.autonomia,
#         "disponible": robot.disponible
#     }
#     for robot in robots
#     }
#     print("Información sobre los robots: ", info_robots)



#     funTFGdisc.simulate_robots(graph, robots, steps)





















