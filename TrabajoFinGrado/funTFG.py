import networkx as nx
import matplotlib.pyplot as plt
import random
import math
from Clases import Nodo, Arista, Robot, Paquete
from gestores import GestionRobots, GestionPaquetes
from reservations import EdgeReservations

def GraphGen(n, m, k, d, rs_rate=1):
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
    nodo_rs1 = Nodo(nombre="RS_1", posicion=(medio, -2), estacion=True, recharge_rate=rs_rate)
    nodo_rs2 = Nodo(nombre="RS_2", posicion=(medio, m + 1), estacion=True, recharge_rate=rs_rate)
    G.add_node(nodo_q1)
    G.add_node(nodo_q2)
    G.add_node(nodo_rs1)
    G.add_node(nodo_rs2)
    G.add_edge(nodo_rs1, nodo_q1, objeto_arista=Arista(nodo_rs1, nodo_q1, peso=2, tipo="pasillo", capacidad=2))
    G.add_edge(nodo_rs2, nodo_q2, objeto_arista=Arista(nodo_rs2, nodo_q2, peso=2, tipo="pasillo", capacidad=2))

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
    max_occupation_array = []
    flujo_paquetes = 1
    sd = .5
    f_min =0.25 #flujo_paquetes-sd
    f_max =0.5 #flujo_paquetes+sd  


    nodo_q1 = next(node for node in graph.nodes if node.nombre == "q1")
    nodo_q2 = next(node for node in graph.nodes if node.nombre == "q2")

    # Inicializar gestores
    gestor_paquetes = GestionPaquetes()
    gestor_robots = GestionRobots(robots, nodo_q1, nodo_q2, graph)
    reservations = EdgeReservations()

    # Inicializar temporizadores para recepción y emisión
    proxima_recepcion = random.uniform(f_min+1, f_max+1) # lowest and highest
    proxima_emision = random.uniform(f_min, f_max)

    # Inicializar robots correctamente
    for robot in robots:
        robot.continuous_position = robot.position.posicion
        robot.paquete_actual = None
        robot.estado = 'espera'
        robot.target = None
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    while current_time < total_time:

         # 1) REINICIAR LA OCUPACIÓN DE TODAS LAS ARISTAS 
        for u, v, data in graph.edges(data=True):
            data["objeto_arista"].ocupacion = 0
        
        # Contabilizar robots que ya estaban recorriendo una arista en el paso
        # anterior para que su ocupación se tenga en cuenta a la hora de decidir
        # si otros robots pueden entrar en la misma.
        for robot in robots:
            if (
                robot.path
                and robot.current_edge_index < len(robot.path) - 1
                and robot.progress_along_edge > 0
            ):
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                arista = graph[start_node][end_node]["objeto_arista"]
                arista.ocupacion += 1
        # Gestión dinámica de llegada y salida de paquetes
        proxima_recepcion -= dt
        proxima_emision -= dt

        if proxima_recepcion <= 0:
            gestor_paquetes.recepcion()
            proxima_recepcion = random.uniform(f_min+1, f_max+1)

        if proxima_emision <= 0:
            estantes = [node for node in graph.nodes if node.estante]
            gestor_paquetes.emision(estantes)
            proxima_emision = random.uniform(f_min, f_max)

        # Asignar tareas dinámicamente a robots
        gestor_robots.asignar_tareas(gestor_paquetes)

        obstacles = {r.position for r in robots if r.estado == 'exhausto'}

        for robot in robots:
            if robot.estado == 'exhausto':
                continue
            if robot.estado == 'recargando':
                robot.recargar(robot.position.recharge_rate)
                if robot.autonomia >= 100:
                    robot.paquete_actual = None
                    robot.destino_final = None
                    gestor_robots.espera(robot)
                continue
            if robot.estado == 'critico' and not getattr(robot.target, 'estacion', False):
                if not gestor_robots.puede_completar_tarea(robot, obstacles):
                    station = gestor_robots.nearest_station(robot.position, obstacles)
                    gestor_robots.enviar_a_estacion(robot, station)

            # Plan route if at node without a planned path
            if (not robot.path or robot.current_edge_index >= len(robot.path) - 1) and robot.target and robot.position != robot.target:
                if not gestor_robots.plan_route(robot, int(current_time / dt), reservations, obstacles):
                    gestor_robots.espera(robot)
                    continue

            if robot.path and robot.current_edge_index < len(robot.path) - 1:
                start_node = robot.path[robot.current_edge_index]
                end_node = robot.path[robot.current_edge_index + 1]
                arista = graph[start_node][end_node]["objeto_arista"]
                scheduled_time = robot.edge_times[robot.current_edge_index]

                if int(current_time / dt) < scheduled_time:
                    continue

                dx = end_node.posicion[0] - start_node.posicion[0]
                dy = end_node.posicion[1] - start_node.posicion[1]
                segment_distance = math.hypot(dx, dy)
                move_distance = speed * dt
                remaining_distance = segment_distance - robot.progress_along_edge

                if robot.progress_along_edge == 0:
                    arista.ocupacion += 1

                if move_distance < remaining_distance:
                    robot.progress_along_edge += move_distance
                    alpha = robot.progress_along_edge / segment_distance
                    robot.continuous_position = (
                        start_node.posicion[0] + alpha * dx,
                        start_node.posicion[1] + alpha * dy,
                    )
                    distancia = move_distance
                else:
                    robot.position = end_node
                    robot.continuous_position = end_node.posicion
                    robot.current_edge_index += 1
                    robot.progress_along_edge = 0.0
                    distancia = remaining_distance
                    reservations.release_before(int(current_time / dt))

                robot.consumir_energia(
                    distancia,
                    robot.paquete_actual.peso if robot.paquete_actual else 0,
                )

            # Lógica cuando el robot llega a un destino
            if robot.target and robot.position == robot.target:
                if getattr(robot.target, 'estacion', False):
                    gestor_robots.iniciar_recarga(robot)
                    continue
                if robot.estado == 'recogida' and robot.position == nodo_q1:
                    robot.paquete_actual.posicion = robot.continuous_position
                    paquetes_visuales.append(robot.paquete_actual)
                    gestor_robots.almacenamiento(robot, robot.destino_final)
                  

                elif robot.estado == 'almacenamiento':
                    try:    
                        robot.position.añadir_paquete(robot.paquete_actual)
                        paquetes_visuales.remove(robot.paquete_actual)
                        robot.paquete_actual = None
                        robot.destino_final = None
                        gestor_robots.espera(robot)
                    except:
                        gestor_robots.reasignacion(
                            robot,
                            gestor_paquetes,
                            paquetes_visuales,
                            int(current_time / dt),
                            reservations,
                            obstacles,
                        )
                    

                elif robot.estado == 'buscar':
                    paquete_recogido = robot.position.retirar_paquete()
                    if paquete_recogido:
                        robot.paquete_actual = paquete_recogido
                        robot.paquete_actual.posicion = robot.continuous_position
                        paquetes_visuales.append(robot.paquete_actual)
                    gestor_robots.salida(robot)

                elif robot.estado == 'salida' and robot.position == nodo_q2:
                    if robot.paquete_actual in paquetes_visuales:
                        paquetes_visuales.remove(robot.paquete_actual)
                    robot.paquete_actual = None
                    robot.destino_final = None
                    gestor_robots.espera(robot)

        # Actualizar posiciones visuales de los paquetes en movimiento
        for robot in robots:
            if robot.paquete_actual:
                robot.paquete_actual.posicion = robot.continuous_position

        # BUSCAR LA OCUPACIÓN MÁXIMA DE LAS ARISTAS Y GUARDARLA EN max_occupation_array
        max_occupancy = 0
        for _, _, data in graph.edges(data=True):
            if data["objeto_arista"].ocupacion > max_occupancy:
                max_occupancy = data["objeto_arista"].ocupacion
        max_occupation_array.append(max_occupancy)

        # Estado visual de almacenamiento (estantes)
        estado_almacenamiento = {}
        for node in graph.nodes:
            if node.estante:
                cantidad = node.get_cantidad()
                estado_almacenamiento[node.nombre] = (node.posicion, cantidad)

        # Snapshot visual
        snapshot = {
            'robots': {robot.id: (robot.continuous_position, robot.estado) for robot in robots},
            'paquetes': [p.posicion for p in paquetes_visuales],
            'almacenamiento': estado_almacenamiento
        }

        simulation_data.append(snapshot)
        current_time += dt

    return simulation_data,max_occupation_array
                


def playback_simulation(graph, simulation_data, dt=0.1):
    plt.ion()
    fig, ax = plt.subplots(figsize=(12,12))
    pos = {node: node.posicion for node in graph.nodes()}

    for snapshot in simulation_data:
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=400, node_color="lightgray", ax=ax)

        robot_positions = [pos for pos, _ in snapshot['robots'].values()]
        robot_colors = []
        for _, estado in snapshot['robots'].values():
            if estado == 'exhausto':
                robot_colors.append('black')
            elif estado in ['critico', 'recargando']:
                robot_colors.append('yellow')
            else:
                robot_colors.append('red')
        ax.scatter(*zip(*robot_positions), color=robot_colors, s=750, label="Robots")

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


