import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq
import math
from Clases import Nodo,Arista,Robot,Paquete

def GraphGen(n, m, k, d):
    """
    Crea un grafo que representa un almacén.
    """
    if k > n * m:
        raise ValueError("El número de ubicaciones k no puede exceder el espacio total disponible n * m.")
    if d >= (k // n) + (1 if k % n > 0 else 0):
        raise ValueError("El desahogo debe estar dentro de la cantidad de ubicaciones por hilera.")

    medio = (n - 1) / 2
    if n % 2 == 0:
        medio = n / 2 - 0.5

    G = nx.Graph()

    # Nodos de entrada y salida
    nodo_q1 = Nodo(nombre=str((medio,-1)), posicion=(medio, -1), peso=1, altura=2)
    nodo_q2 = Nodo(nombre="q2", posicion=(medio, m), peso=1, altura=2)
    G.add_node(nodo_q1)
    G.add_node(nodo_q2)

    # Distribución de ubicaciones en hileras
    ubicaciones_por_hilera = [k // n] * n
    for i in range(k % n):
        ubicaciones_por_hilera[i] += 1

    nodo_id = 1  
    hileras = []
    for i in range(n):
        hilera = []
        for j in range(ubicaciones_por_hilera[i]):
            nombre = str((i,j))#f"u{nodo_id}"
            estante = {'posEstante': (i, j), 'producto': 'nada', 'Completo': False}
            nodo = Nodo(nombre=nombre, posicion=(i, j), estante=estante)
            G.add_node(nodo)
            hilera.append(nodo)
            nodo_id += 1
        hileras.append(hilera)

    # Conectar nodos dentro de cada hilera
    for hilera in hileras:
        for i in range(len(hilera) - 1):
            pasillo = Arista(hilera[i], hilera[i+1], peso=2, tipo="pasillo", capacidad=2)
            G.add_edge(hilera[i], hilera[i+1], objeto_arista=pasillo)

    # Conexión entre extremos de hileras adyacentes
    for i in range(len(hileras) - 1):
        pas1 = Arista(hileras[i][0], hileras[i+1][0], peso=2, tipo="pasillo", capacidad=2)
        pas2 = Arista(hileras[i][-1], hileras[i+1][-1], peso=2, tipo="pasillo", capacidad=2)
        G.add_edge(hileras[i][0], hileras[i+1][0], objeto_arista=pas1)
        G.add_edge(hileras[i][-1], hileras[i+1][-1], objeto_arista=pas2)

    # Conectar nodo de entrada con la primera ubicación de cada hilera
    for hilera in hileras:
        pasEntrada = Arista(nodo_q1, hilera[0], peso=2, tipo="pasillo", capacidad=2)
        G.add_edge(nodo_q1, hilera[0], objeto_arista=pasEntrada)

    # Conectar nodo de salida con la última ubicación de cada hilera
    for hilera in hileras:
        pasSalida = Arista(nodo_q2, hilera[-1], peso=2, tipo="pasillo", capacidad=2)
        G.add_edge(nodo_q2, hilera[-1], objeto_arista=pasSalida)

    # Creación de pasillos de desahogo
    for i in range(d):
        for j in range(n - 1):
            desahogo_nodo = Nodo(
                nombre=f"d{i}_{j}",
                posicion=(j + 0.5, (m / (d + 1)) * (i + 1) - 0.5),
                peso=1,
                altura=2
            )
            G.add_node(desahogo_nodo)
            ubicacion_corte = (m // (d + 1)) * (i + 1) - 1
            for k_index in range(j, j + 2):
                if k_index < len(hileras):
                    if ubicacion_corte < len(hileras[k_index]) - 1:
                        pasD1 = Arista(desahogo_nodo, hileras[k_index][ubicacion_corte], peso=2, tipo="pasillo", capacidad=2)
                        pasD2 = Arista(desahogo_nodo, hileras[k_index][ubicacion_corte + 1], peso=2, tipo="pasillo", capacidad=2)
                        G.add_edge(desahogo_nodo, hileras[k_index][ubicacion_corte], objeto_arista=pasD1)
                        G.add_edge(desahogo_nodo, hileras[k_index][ubicacion_corte + 1], objeto_arista=pasD2)
            if j > 0:
                for node in G.nodes():
                    if isinstance(node, Nodo) and node.nombre == f"d{i}_{j-1}":
                        pasEx = Arista(desahogo_nodo, node, peso=2, tipo="pasillo", capacidad=2)
                        G.add_edge(desahogo_nodo, node, objeto_arista=pasEx)
                        break

    return G

def create_robots(num_robots, graph):
    nodes = list(graph.nodes())
    robots = []
    for i in range(num_robots):
        start_node = random.choice(nodes)
        robot = Robot(id=i + 1, position=start_node)
        robots.append(robot)
    return robots

def a_star_search(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for neighbor in graph.neighbors(current):
            arista = graph[current][neighbor]['objeto_arista']
            new_cost = cost_so_far[current] + arista.get_peso()
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))
                came_from[neighbor] = current

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    return path[::-1]

def simulate_robots_continuous(graph, robots, total_time, dt=0.1, speed=1):
    """
    Calcula la simulación en dominio continuo, almacenando un snapshot del estado (posición continua de cada robot)
    en cada intervalo dt.
    """
    simulation_data = []
    current_time = 0.0

    # Inicializar la posición continua de cada robot
    for robot in robots:
        robot.continuous_position = robot.position.posicion
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    while current_time < total_time:
        # Asignar destino a robots sin target
        for robot in robots:
            if robot.target is None:
                target = random.choice(list(graph.nodes()))
                robot.set_target(target)
                robot.path = a_star_search(graph, robot.position, robot.target)
                robot.current_edge_index = 0
                robot.progress_along_edge = 0.0

        # Actualizar la posición continua para cada robot
        for robot in robots:
            if robot.target and robot.path and robot.current_edge_index < len(robot.path) - 1:
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                start_pos = start_node.posicion
                end_pos = end_node.posicion
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                segment_distance = math.sqrt(dx**2 + dy**2)
                distance_to_move = speed * dt
                remaining_distance = segment_distance - robot.progress_along_edge
                if distance_to_move < remaining_distance:
                    robot.progress_along_edge += distance_to_move
                    alpha = robot.progress_along_edge / segment_distance
                    new_x = start_pos[0] + alpha * dx
                    new_y = start_pos[1] + alpha * dy
                    robot.continuous_position = (new_x, new_y)
                else:
                    # Completa el segmento actual
                    robot.position = end_node  # Actualización discreta del nodo
                    robot.continuous_position = end_node.posicion
                    robot.current_edge_index += 1
                    robot.progress_along_edge = 0.0
                    if robot.current_edge_index >= len(robot.path) - 1:
                        robot.target = None
                        robot.path = []
                        robot.current_edge_index = 0
        # Guardar snapshot del estado actual
        snapshot = {robot.id: robot.continuous_position for robot in robots}
        # snapshot = [robot.continuous_position for robot in robots] #--------------------------------
        simulation_data.append(snapshot)
        current_time += dt

    return simulation_data

def playback_simulation(graph, simulation_data, dt=0.1):
    """
    Reproduce la simulación a partir de los snapshots calculados.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = {node: node.posicion for node in graph.nodes()}
    
    for snapshot in simulation_data:
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=350, node_color="lightblue")
        robot_positions = list(snapshot.values())
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")
        ax.legend(loc="upper left", fontsize=12, frameon=True)
        plt.pause(dt)
    
    plt.ioff()
    plt.show()
