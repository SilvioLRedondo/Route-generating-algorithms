
import funTFG
from funAuxTFG import guardar_informacion,cargar_informacion
from reservations import EdgeReservations, HileraReservations
import plot_metrics as pm


if __name__ == "__main__":
    n, m, k, d = 4, 4, 16, 1
    num_robots = 5
    consumo_robot = 0.5
    tsam = 0.1
    total_simulation_time = 100
    carga_inicial = 0.1
    recharge_rate = 1
    MAX_HILERA_H = 20
    HILERA_DEFAULT_CAPACITY = 3
    HILERA_COLUMN_CAPACITY = {}
    
    # Generación del grafo del almacén
    graph = funTFG.GraphGen(n, m, k, d, rs_rate=recharge_rate)

    # Inicialización aleatoria del almacén 
    funTFG.inicializar_almacen(graph, carga_inicial)

    # Crear robots
    robots = funTFG.create_robots(num_robots, graph, consumo_robot=consumo_robot)

    edge_reserv = EdgeReservations()
    hilera_reserv = HileraReservations(HILERA_DEFAULT_CAPACITY, HILERA_COLUMN_CAPACITY)

    # Simulación completa 
    simulation_data, metrics = funTFG.simulate_robots_continuous(
        graph,
        robots,
        total_simulation_time,
        edge_reserv,
        hilera_reserv,
        MAX_HILERA_H,
        dt=tsam,
        speed=1,
    )

    time = len(metrics["max_corridor_occupancy"])
    # print("El tiempo es:", time)
    
    print(metrics['robot_state_time'])
    
    pm.visualizar_metricas(metrics, dt=tsam, save_dir=None, show=True)
    
    
    funTFG.playback_simulation(graph, simulation_data, dt=tsam)

    # time = len(max_occupation_array)
    # media = sum(max_occupation_array)/time
    # print(max_occupation_array,media)
    

    # tiempoActividad = tiempos_de_estados['actividad']

    # print(tiempoActividad)

    # Visualización
    


    
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
   







