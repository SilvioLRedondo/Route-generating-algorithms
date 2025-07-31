import networkx as nx
import random
import matplotlib.pyplot as plt


def GraphGen(n, m, k, d):
    """
    Crea un grafo que representa un almacén con dimensiones n x m, k ubicaciones de almacenamiento
    y un desahogo en la posición d.

    Entradas:
        n (int): Número de hileras (ancho del almacén).
        m (int): Largo del almacén (número máximo de ubicaciones por hilera).
        k (int): Número total de ubicaciones de almacenamiento.
        d (int): Posición del desahogo (debe ser menor que la cantidad de ubicaciones por hilera).

    Salida:
        G (networkx.Graph): Grafo generado.
    """
    if k > n * m:
        raise ValueError("El número de ubicaciones k no puede exceder el espacio total disponible n * m.")
    if d >= (k // n) + (1 if k % n > 0 else 0):
        raise ValueError("El desahogo debe estar dentro de la cantidad de ubicaciones por hilera.")

    G = nx.Graph()
    
    # Nodos de entrada y salida
    G.add_node("q1")  # Entrada
    G.add_node("q2")  # Salida

    # Distribuir ubicaciones en las hileras
    ubicaciones_por_hilera = [k // n] * n
    for i in range(k % n):
        ubicaciones_por_hilera[i] += 1

    # Crear las ubicaciones y conectarlas
    nodo_id = 1  
    hileras = []

    for i in range(n):
        hilera = []
        for j in range(ubicaciones_por_hilera[i]):
            nodo = f"u{nodo_id}"
            G.add_node(nodo)
            hilera.append(nodo)
            nodo_id += 1
        hileras.append(hilera)

    # Conectar nodos dentro de las hileras
    for hilera in hileras:
        for i in range(len(hilera) - 1):
            G.add_edge(hilera[i], hilera[i + 1])

    # Conexión entre extremos de las hileras
    for i in range(len(hileras) - 1):
        G.add_edge(hileras[i][0], hileras[i + 1][0])  # Entrada de hilera i con i+1
        G.add_edge(hileras[i][-1], hileras[i + 1][-1])  # Salida de hilera i con i+1
    
    # Conectar entrada del almacén con las primeras ubicaciones de cada hilera
    for hilera in hileras:
        G.add_edge("q1", hilera[0])

    # Conectar salida del almacén con las últimas ubicaciones de cada hilera
    for hilera in hileras:
        G.add_edge("q2", hilera[-1])
    
    # Creación de pasillos esto lo dejo por si fuera de utilidad, actualmente
    # todo esto se hace en el siguiente bucle, esto es útil para visualizar 
    # el pasillo

    ubicaciones_corte=[]
    for i in range(d):
        a = (m//(d+1))*(i+1)
        ubicaciones_corte.append(a)
    # Conectar nodos adyacentes en la columna del desahogo
    if d >= 0:
        for i in range(d):#range(len(hileras)):
            if d < m:#len(hileras[i]):
                desahogo_nodo = f"d{i}"
                G.add_node(desahogo_nodo)
                ubicacion_corte = (m//(d+1))*(i+1) -1

                for j in range(n):
                    G.add_edge(desahogo_nodo, hileras[j][ubicacion_corte])
                    G.add_edge(desahogo_nodo, hileras[j][ubicacion_corte+1])
    
    return G


def create_robots(num_robots, graph):
    """
    Crea una lista de robots ubicados en nodos aleatorios del grafo.

    Entradas:
        num_robots (int): Número de robots a crear.
        graph (networkx.Graph): Grafo del almacén.

    Salida:
        robots (list): Lista de robots con posiciones iniciales aleatorias.
    """
    nodes = list(graph.nodes)
    robots = []
    
    for i in range(num_robots):
        start_node = random.choice(nodes)
        robot = {"id": i, "position": start_node}
        robots.append(robot)
    
    return robots

def simulate_robots(graph, robots, steps):
    """
    Simula el movimiento de los robots en el almacén.
    
    Cada robot se mueve aleatoriamente a un nodo vecino en cada paso.
    """
    plt.ion()  # Modo interactivo de matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(graph, seed=42)

    for step in range(steps):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=500, node_color="lightblue")

        # Mover los robots a un nodo vecino aleatorio
        for robot in robots:
            neighbors = list(graph.neighbors(robot["position"]))
            if neighbors:
                robot["position"] = random.choice(neighbors)

        # Dibujar robots
        robot_positions = [pos[robot["position"]] for robot in robots]
        ax.scatter(*zip(*robot_positions), color="red", s=100, label="Robots")

        plt.legend()
        plt.pause(0.5)  # Esperar medio segundo entre cada actualización

    plt.ioff()  # Desactivar modo interactivo
    plt.show()
