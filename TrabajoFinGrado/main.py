
import funTFG
from funAuxTFG import guardar_informacion,cargar_informacion
from reservations import EdgeReservations, HileraReservations
import plot_metrics as pm
import random
random.seed(225288) 

if __name__ == "__main__":
    n, m, k, d = 12, 12, 144, 1
    num_robots = 70
    
    
    consumo_robot = 0.12 # 0.12
    tsam = 0.1
    total_simulation_time = 100

    carga_inicial = 0.5
    
    recharge_rate = 1
    MAX_HILERA_H = 20
    HILERA_DEFAULT_CAPACITY = 2
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

    # Representación de la simulación
    funTFG.playback_simulation(graph, simulation_data, dt=tsam)

    # Representación de métricas
    pm.visualizar_metricas(metrics, tsim=total_simulation_time, dt=tsam, save_dir=None, show=True)
    
    
