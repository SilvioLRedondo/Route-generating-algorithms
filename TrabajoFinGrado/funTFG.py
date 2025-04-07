import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq
import math
from algoritmos import a_star_search
from Clases import Nodo,Arista,Robot,Paquete,GestionRobots,GestionPaquetes

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
    nodo_q1 = Nodo(nombre="q1", posicion=(medio, -1), peso=1, altura=2)
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
            nombre = f"u{nodo_id}"
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


def inicializar_almacen(graph, carga_inicial):
    """
    Inicializa los estantes del almacén según el nivel de carga inicial especificado.
    
    :param graph: grafo del almacén generado previamente.
    :param carga_inicial: valor entre 0 (vacío) y 1 (totalmente lleno).
    """
    estantes = [node for node in graph.nodes if node.estante]

    # Calcular el número de estantes a ocupar según carga inicial
    num_estantes_ocupados = int(len(estantes) * carga_inicial)

    # Elegir aleatoriamente qué estantes estarán ocupados
    estantes_ocupados = random.sample(estantes, num_estantes_ocupados)

    for estante in estantes_ocupados:
        cantidad_paquetes = random.randint(1, 10)  # Cantidad aleatoria entre 1 y 10
        producto_aleatorio = random.choice(Paquete.productos_disponibles)
        estante.almacenamiento = (producto_aleatorio, cantidad_paquetes)

    # Asegurar que el resto de estantes estén vacíos
    for estante in estantes:
        if estante not in estantes_ocupados:
            estante.almacenamiento = None



def create_robots(num_robots, graph):
    nodes = list(graph.nodes())
    robots = []
    for i in range(num_robots):
        start_node = random.choice(nodes)
        robot = Robot(id=i + 1, position=start_node)
        robots.append(robot)
    return robots


def simulate_robots_continuous(graph, robots, total_time, dt=0.1, speed=1):
    simulation_data = []
    paquetes_visuales = []
    current_time = 0.0

    nodo_q1 = next(node for node in graph.nodes if node.nombre == "q1")
    nodo_q2 = next(node for node in graph.nodes if node.nombre == "q2")

    # Inicializar gestores
    gestor_paquetes = GestionPaquetes()
    gestor_robots = GestionRobots(robots, nodo_q1, nodo_q2, graph)

    # Inicializar temporizadores para recepción y emisión
    proxima_recepcion = random.uniform(0.5, 2.0)
    proxima_emision = random.uniform(1.0, 3.0)

    # Inicializar robots correctamente
    for robot in robots:
        robot.continuous_position = robot.position.posicion
        robot.paquete_actual = None
        robot.estado = 'espera'
        robot.target = None
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    while current_time < total_time:
        # Gestión dinámica de llegada y salida de paquetes
        proxima_recepcion -= dt
        proxima_emision -= dt

        if proxima_recepcion <= 0:
            gestor_paquetes.recepcion()
            proxima_recepcion = random.uniform(0.5, 2.0)

        if proxima_emision <= 0:
            estantes = [node for node in graph.nodes if node.estante]
            gestor_paquetes.emision(estantes)
            proxima_emision = random.uniform(1.0, 3.0)

        # Asignar tareas dinámicamente a robots
        gestor_robots.asignar_tareas(gestor_paquetes)

        for robot in robots:
            # Movimiento continuo
            if robot.path and robot.current_edge_index < len(robot.path) - 1:
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                dx, dy = end_node.posicion[0] - start_node.posicion[0], end_node.posicion[1] - start_node.posicion[1]
                segment_distance = math.hypot(dx, dy)
                move_distance = speed * dt
                remaining_distance = segment_distance - robot.progress_along_edge

                if move_distance < remaining_distance:
                    robot.progress_along_edge += move_distance
                    alpha = robot.progress_along_edge / segment_distance
                    new_pos = (start_node.posicion[0] + alpha * dx,
                               start_node.posicion[1] + alpha * dy)
                    robot.continuous_position = new_pos
                else:
                    robot.position = end_node
                    robot.continuous_position = end_node.posicion
                    robot.current_edge_index += 1
                    robot.progress_along_edge = 0.0

            # Lógica cuando el robot llega a un destino
            if robot.target and robot.position == robot.target:
                if robot.estado == 'recogida' and robot.position == nodo_q1:
                    robot.paquete_actual.posicion = robot.continuous_position
                    paquetes_visuales.append(robot.paquete_actual)
                    gestor_robots.almacenamiento(robot, robot.destino_final)

                elif robot.estado == 'almacenamiento':
                    robot.position.añadir_paquete(robot.paquete_actual)
                    paquetes_visuales.remove(robot.paquete_actual)
                    robot.paquete_actual = None
                    robot.destino_final = None
                    gestor_robots.espera(robot)

                elif robot.estado == 'buscar':
                    robot.paquete_actual.posicion = robot.continuous_position
                    paquetes_visuales.append(robot.paquete_actual)
                    gestor_robots.salida(robot)

                elif robot.estado == 'salida' and robot.position == nodo_q2:
                    paquetes_visuales.remove(robot.paquete_actual)
                    robot.paquete_actual = None
                    robot.destino_final = None
                    gestor_robots.espera(robot)

        # Actualizar posiciones visuales de los paquetes en movimiento
        for robot in robots:
            if robot.paquete_actual:
                robot.paquete_actual.posicion = robot.continuous_position

        # Estado visual de almacenamiento (estantes)
        estado_almacenamiento = {}
        for node in graph.nodes:
            if node.estante:
                cantidad = node.get_cantidad()
                estado_almacenamiento[node.nombre] = (node.posicion, cantidad)

        # Snapshot visual
        snapshot = {
            'robots': {robot.id: robot.continuous_position for robot in robots},
            'paquetes': [p.posicion for p in paquetes_visuales],
            'almacenamiento': estado_almacenamiento
        }

        simulation_data.append(snapshot)
        current_time += dt

    return simulation_data
                

def simulate_robots_continuous1(graph, robots, total_time, dt=0.1, speed=1):
    simulation_data = []
    paquetes_visuales = []
    current_time = 0.0

    nodo_q1 = next(node for node in graph.nodes if node.nombre == "q1")
    nodo_q2 = next(node for node in graph.nodes if node.nombre == "q2")

    paquetes_generados = [Paquete(posicion=nodo_q1.posicion) for _ in range(5)]
    paquetes_visuales.extend(paquetes_generados)

    # Inicialización ajustada en simulate_robots_continuous
    for robot in robots:
        robot.continuous_position = robot.position.posicion
        robot.paquete_actual = None
        robot.target = None
        robot.estado = 'espera'  # claramente definido el estado inicial
        robot.destino_final = None
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
    
    # Crear objeto gestor de paquetes
    gestor_paquetes = GestionPaquetes()

    # Prueba inicial de recepción (crear paquetes)
    for _ in range(3):
        gestor_paquetes.recepcion()

    # Prueba inicial de emisión (solicitar paquetes del almacén)
    estantes = [node for node in graph.nodes if node.estante]
    for _ in range(3):
        gestor_paquetes.emision(estantes)

    # Comprobar las colas:
    print("\nPaquetes en cola de recepción (q1):")
    for paquete in gestor_paquetes.cola_recepcion:
        print("-", paquete.producto)

    print("\nPaquetes en cola de emisión (desde estantes):")
    for paquete, estante in gestor_paquetes.cola_emision:
        print(f"- {paquete.producto} (desde estante {estante.nombre})")

    # Definir nodos q1 y q2 del grafo
    nodo_q1 = next(node for node in graph.nodes if node.nombre == "q1")
    nodo_q2 = next(node for node in graph.nodes if node.nombre == "q2")

    # Crear objeto gestor de robots
    gestor_robots = GestionRobots(robots, nodo_q1, nodo_q2, graph)

    # Ejemplo inicial de asignación
    gestor_robots.asignar_tareas(gestor_paquetes)

    # Comprobar visualmente (o mediante prints)
    for robot in robots:
        print(f"Robot {robot.id} estado: {robot.estado}, target: {robot.target}")

    while current_time < total_time:
        for robot in robots:

            # Caso A: Robot sin paquete ni tarea asignada
            if robot.paquete_actual is None and robot.target is None:
                # Prioridad: primero sacar paquete de estante a q2
                estantes_con_paquetes = [node for node in graph.nodes if node.estante and node.get_cantidad() > 0]
                if estantes_con_paquetes:
                    robot.target = random.choice(estantes_con_paquetes)
                elif paquetes_generados:  # Sino, ir a recoger paquetes nuevos en q1
                    robot.target = nodo_q1

                if robot.target:
                    robot.path = a_star_search(graph, robot.position, robot.target)
                    robot.current_edge_index = 0
                    robot.progress_along_edge = 0.0

            # Caso B: Robot recogiendo paquete desde q1 o estante
            if robot.paquete_actual is None and robot.position == robot.target:
                if robot.position == nodo_q1 and paquetes_generados:
                    robot.paquete_actual = paquetes_generados.pop(0)
                    destinos_posibles = [node for node in graph.nodes if node.estante and node.get_cantidad() < 10]
                    if destinos_posibles:
                        robot.target = random.choice(destinos_posibles)
                        robot.path = a_star_search(graph, robot.position, robot.target)
                        robot.current_edge_index = 0
                        robot.progress_along_edge = 0.0
                elif robot.position.estante and robot.position.get_cantidad() > 0:
                    robot.paquete_actual = robot.position.retirar_paquete()
                    paquetes_visuales.append(robot.paquete_actual)
                    robot.target = nodo_q2
                    robot.path = a_star_search(graph, robot.position, nodo_q2)
                    robot.current_edge_index = 0
                    robot.progress_along_edge = 0.0

            # Caso C: Robot depositando paquete en estante o en q2
            if robot.paquete_actual and robot.position == robot.target:
                if robot.target == nodo_q2:
                    paquetes_visuales.remove(robot.paquete_actual)
                elif robot.position.estante and robot.position.get_cantidad() > 0:
                    robot.paquete_actual = robot.position.retirar_paquete()
                    robot.paquete_actual.posicion = robot.continuous_position
                    paquetes_visuales.append(robot.paquete_actual)  # Añadir visualmente el paquete aquí (clave)
                    robot.target = nodo_q2
                    robot.path = a_star_search(graph, robot.position, nodo_q2)
                    robot.current_edge_index = 0
                    robot.progress_along_edge = 0.0
                else:
                    robot.position.añadir_paquete(robot.paquete_actual)
                    paquetes_visuales.remove(robot.paquete_actual)
                
                robot.paquete_actual = None
                robot.target = None
                

            # Movimiento continuo
            if robot.path and robot.current_edge_index < len(robot.path) - 1:
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                dx, dy = end_node.posicion[0] - start_node.posicion[0], end_node.posicion[1] - start_node.posicion[1]
                segment_distance = math.hypot(dx, dy)
                move_distance = speed * dt
                remaining_distance = segment_distance - robot.progress_along_edge

                if move_distance < remaining_distance:
                    robot.progress_along_edge += move_distance
                    alpha = robot.progress_along_edge / segment_distance
                    new_pos = (start_node.posicion[0] + alpha * dx,
                               start_node.posicion[1] + alpha * dy)
                    robot.continuous_position = new_pos
                else:
                    robot.position = end_node
                    robot.continuous_position = end_node.posicion
                    robot.current_edge_index += 1
                    robot.progress_along_edge = 0.0

            if robot.paquete_actual:
                robot.paquete_actual.posicion = robot.continuous_position

        # Estado visual de almacenamiento (Estantes)
        estado_almacenamiento = {}
        for node in graph.nodes:
            if node.estante:
                cantidad = node.get_cantidad()
                estado_almacenamiento[node.nombre] = (node.posicion, cantidad)

        snapshot = {
            'robots': {robot.id: robot.continuous_position for robot in robots},
            'paquetes': [paquete.posicion for paquete in paquetes_visuales],
            'almacenamiento': estado_almacenamiento
        }

        simulation_data.append(snapshot)
        current_time += dt

    return simulation_data


def simulate_robots_continuous1(graph, robots, total_time, dt=0.1, speed=1):
    simulation_data = []
    paquetes_visuales = []
    current_time = 0.0

    # Encontrar nodo q1 y q2
    nodo_q1 = next(node for node in graph.nodes if node.nombre == "q1")
    nodo_q2 = next(node for node in graph.nodes if node.nombre == "q2")

    # Inicialmente, 5 paquetes visualmente creados en q1
    paquetes_generados = [Paquete(posicion=nodo_q1.posicion) for _ in range(5)]
    paquetes_visuales.extend(paquetes_generados)

    # Inicialización correcta de robots
    for robot in robots:
        robot.continuous_position = robot.position.posicion
        robot.paquete_actual = None
        robot.target = None
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    while current_time < total_time:
        for robot in robots:
            # Caso 1: Robot sin tarea (sin paquete, sin objetivo)
            if robot.target is None and robot.paquete_actual is None:
                if paquetes_generados:
                    robot.target = nodo_q1
                    robot.path = a_star_search(graph, robot.position, nodo_q1)
                    robot.current_edge_index = 0
                    robot.progress_along_edge = 0.0

            # Caso 2: Robot en q1, recogiendo paquete
            if robot.position == nodo_q1 and robot.paquete_actual is None:
                if paquetes_generados:
                    robot.paquete_actual = paquetes_generados.pop(0)
                    # Elegir destino (estante con espacio disponible)
                    estantes_validos = [node for node in graph.nodes if node.estante and node.get_cantidad() < 10]
                    if estantes_validos:
                        robot.target = random.choice(estantes_validos)
                        robot.path = a_star_search(graph, robot.position, robot.target)
                        robot.current_edge_index = 0
                        robot.progress_along_edge = 0.0

            # Caso 3: Robot en estante, dejando paquete
            if robot.paquete_actual and robot.position == robot.target and robot.target != nodo_q1:
                robot.position.añadir_paquete(robot.paquete_actual)
                paquetes_visuales.remove(robot.paquete_actual)
                robot.paquete_actual = None
                robot.target = None

            # Movimiento continuo del robot
            if robot.path and robot.current_edge_index < len(robot.path) - 1:
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                dx, dy = end_node.posicion[0] - start_node.posicion[0], end_node.posicion[1] - start_node.posicion[1]
                segment_distance = math.hypot(dx, dy)
                move_distance = speed * dt
                remaining_distance = segment_distance - robot.progress_along_edge

                if move_distance < remaining_distance:
                    robot.progress_along_edge += move_distance
                    alpha = robot.progress_along_edge / segment_distance
                    new_pos = (start_node.posicion[0] + alpha * dx,
                               start_node.posicion[1] + alpha * dy)
                    robot.continuous_position = new_pos
                else:
                    # Completar movimiento hacia el nodo siguiente
                    robot.position = end_node
                    robot.continuous_position = end_node.posicion
                    robot.current_edge_index += 1
                    robot.progress_along_edge = 0.0

            # Movimiento visual del paquete con robot
            if robot.paquete_actual:
                robot.paquete_actual.posicion = robot.continuous_position

        # Snapshot visual actualizado
        snapshot = {
            'robots': {robot.id: robot.continuous_position for robot in robots},
            'paquetes': [paquete.posicion for paquete in paquetes_visuales]
        }
        simulation_data.append(snapshot)
        current_time += dt

    return simulation_data

def playback_simulation(graph, simulation_data, dt=0.1):
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = {node: node.posicion for node in graph.nodes()}

    for snapshot in simulation_data:
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=400, node_color="lightgray", ax=ax)

        # Robots en rojo
        robot_positions = list(snapshot['robots'].values())
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")

        # Paquetes en azul
        paquete_positions = snapshot['paquetes']
        if paquete_positions:
            ax.scatter(*zip(*paquete_positions), color="blue", s=500, label="Paquetes")

        # Representación visual de almacenamiento
        for nombre, (posicion, cantidad) in snapshot['almacenamiento'].items():
            if cantidad == 0:
                continue  # No mostrar círculo si está vacío
            elif cantidad == 10:
                ax.scatter(*posicion, s=550, facecolors='none', edgecolors='green', linewidths=2, label="Estante lleno" if "Estante lleno" not in ax.get_legend_handles_labels()[1] else "")
            else:
                ax.scatter(*posicion, s=400, facecolors='none', edgecolors='orange', linewidths=2, label="Estante parcial" if "Estante parcial" not in ax.get_legend_handles_labels()[1] else "")

        ax.legend(loc="upper left", fontsize=12, frameon=True)
        plt.pause(dt)

    plt.ioff()
    plt.show()


def playback_simulation1(graph, simulation_data, dt=0.1):
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = {node: node.posicion for node in graph.nodes()}
    
    for snapshot in simulation_data:
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=400, node_color="lightgray", ax=ax)

        # Dibujar robots
        robot_positions = list(snapshot['robots'].values())
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")

        # Dibujar paquetes
        paquete_positions = snapshot['paquetes']
        if paquete_positions:
            ax.scatter(*zip(*paquete_positions), color="blue", s=500, label="Paquetes")

        ax.legend(loc="upper left", fontsize=12, frameon=True)
        plt.pause(dt)
    
    plt.ioff()
    plt.show()

