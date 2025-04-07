import funTFG
from funAuxTFG import guardar_informacion,cargar_informacion



if __name__ == "__main__":
    n, m, k, d = 8, 6, 48, 1
    num_robots = 5
    tsam = 0.1
    total_simulation_time = 400
    carga_inicial = 0
    
    # Generación del grafo del almacén
    graph = funTFG.GraphGen(n, m, k, d)

    # Inicialización aleatoria del almacén 
    funTFG.inicializar_almacen(graph, carga_inicial)

    # Crear robots
    robots = funTFG.create_robots(num_robots, graph)

    # Simulación completa 
    simulation_data = funTFG.simulate_robots_continuous(graph, robots, total_simulation_time, dt=tsam, speed=1)

    # Visualización
    funTFG.playback_simulation(graph, simulation_data, dt=tsam)

    
    # posEstante = {node: node.posicion for node in graph.nodes()}
    # Estantes = {node: node.estante for node in graph.nodes() if hasattr(node, "estante")}
    # pasillos = {
    #     (nodo1, nodo2): {
    #         "peso": data["objeto_arista"].peso,
    #         "tipo": data["objeto_arista"].tipo,
    #         "capacidad": data["objeto_arista"].capacidad,
    #         "longitud": data["objeto_arista"].longitud()
    #     }
    #     for nodo1, nodo2, data in graph.edges(data=True)
    # }
    # print("Información de los nodos:", posEstante, "\n")
    # print("Estantes en los nodos:", Estantes, "\n")
    # print("Información de las aristas:", pasillos, "\n")
    # info_robots = {
    #     robot.id: {
    #         "posición": robot.position,
    #         "objetivo": robot.target,
    #         "distancia": robot.distance,
    #         "capacidad_carga": robot.capacidad_carga,
    #         "autonomía": robot.autonomia,
    #         "disponible": robot.estado
    #     }
    #     for robot in robots
    # }
    # print("Información sobre los robots:", info_robots)
   






























