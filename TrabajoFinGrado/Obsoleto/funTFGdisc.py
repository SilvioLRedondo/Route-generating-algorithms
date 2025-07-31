import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq

class Nodo:
    def __init__(self, nombre, posicion, peso=None, altura=None, estante=None):
        """
        Constructor del nodo.
        
        Parámetros:
          nombre (str): Identificador del nodo (ej. "q1", "u1", "d0_0", etc.).
          posicion (tuple): Posición (x, y) del nodo.
          peso (opcional): Peso asociado.
          altura (opcional): Altura asociada.
          estante (opcional): Información adicional, por ejemplo, en nodos de almacén.
        """
        self.nombre = nombre
        self.posicion = posicion
        self.peso = peso
        self.altura = altura
        self.estante = estante

    def __hash__(self):
        return hash(self.nombre)
    
    def __eq__(self, other):
        return isinstance(other, Nodo) and self.nombre == other.nombre
    
    def __repr__(self):
        return self.nombre

    def __lt__(self, other):
            return self.nombre < other.nombre
    
    # Métodos getters (opcionalmente se pueden definir setters)
    def get_posicion(self):
        return self.posicion

    def get_estante(self):
        return self.estante

class Arista:
    def __init__(self, nodo1, nodo2, peso=1, tipo="normal", capacidad=1, bidireccional=True):
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.tipo = tipo  # Ejemplo: "pasillo", "rampa", "cinta transportadora"
        self.capacidad = capacidad  # Cantidad de robots que pueden pasar simultáneamente
        self.bidireccional = bidireccional

    def __repr__(self):
        return f"Arista({self.nodo1}, {self.nodo2}, peso={self.peso}, tipo={self.tipo})"

    def get_peso(self):
        return self.peso

    def set_peso(self, nuevo_peso):
        self.peso = nuevo_peso

    def longitud(self):
        pos1 = self.nodo1.get_posicion()
        pos2 = self.nodo2.get_posicion()
        return ((pos2[0]-pos1[0])**2 +(pos2[1]-pos1[1])**2)**0.5


class Robot:
    def __init__(self, id, position):
        """
        Constructor del robot.
        
        Parámetros:
          id (int): Identificador único del robot.
          position (Nodo): Nodo en el que se ubica inicialmente el robot.
        """
        self.id = id
        self.position = position  # Objeto de la clase Nodo
        self.target = None
        self.distance = 0
        self.capacidad_carga = 0
        self.autonomia = 100
        self.disponible = True

    def set_target(self, target):
        self.target = target

    def mover(self, nueva_posicion):
        self.position = nueva_posicion

    def __repr__(self):
        return f"Robot {self.id}"


def GraphGen(n, m, k, d):
    """
    Crea un grafo que representa un almacén con dimensiones n x m, k ubicaciones de almacenamiento
    y tantos pasillos de desahogo como indique d.

    Entradas:
        n (int): Número de hileras (ancho del almacén).
        m (int): Largo del almacén (número máximo de ubicaciones por hilera).
        k (int): Número total de ubicaciones de almacenamiento. No puede ser superior a n*m.
        d (int): Número de pasillos de desahogo. Debe ser un entero menor que el mayor divisor de m.

    Salida:
        G (networkx.Graph): Grafo generado.
    """
    if k > n * m:
        raise ValueError("El número de ubicaciones k no puede exceder el espacio total disponible n * m.")
    if d >= (k // n) + (1 if k % n > 0 else 0):
        raise ValueError("El desahogo debe estar dentro de la cantidad de ubicaciones por hilera.")

    medio = (n - 1) / 2
   
    if n % 2 == 0:
        medio = n / 2 - 0.5

    G = nx.Graph()

    # Crear nodos de entrada y salida
    nodo_q1 = Nodo(nombre="q1", posicion=(medio, -1), peso=1, altura=2)
    nodo_q2 = Nodo(nombre="q2", posicion=(medio, m), peso=1, altura=2)
    a,b = nodo_q1.get_posicion()
    
    G.add_node(nodo_q1)
    G.add_node(nodo_q2)

    # Distribuir ubicaciones en las hileras
    ubicaciones_por_hilera = [k // n] * n
    for i in range(k % n):
        ubicaciones_por_hilera[i] += 1

    # Crear las ubicaciones y agregarlas al grafo
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
            pasillo = Arista(hilera[i],hilera[i+1],peso=2, tipo="pasillo", capacidad=2)
            G.add_edge(hilera[i], hilera[i + 1],objeto_arista = pasillo)


    # Conexión entre extremos de hileras adyacentes
    for i in range(len(hileras) - 1):
        pas1 = Arista(hileras[i][0],hileras[i+1][0],peso=2, tipo="pasillo", capacidad=2)
        pas2 = Arista(hileras[i][-1], hileras[i + 1][-1],peso=2, tipo="pasillo", capacidad=2)
        G.add_edge(hileras[i][0], hileras[i + 1][0], objeto_arista = pas1)
        G.add_edge(hileras[i][-1], hileras[i + 1][-1], objeto_arista = pas2)

    # Conectar nodo de entrada con la primera ubicación de cada hilera
    for hilera in hileras:
        pasEntrada = Arista(nodo_q1, hilera[0],peso=2, tipo="pasillo", capacidad=2)
        G.add_edge(nodo_q1, hilera[0], objeto_arista=pasEntrada)


    # Conectar nodo de salida con la última ubicación de cada hilera
    for hilera in hileras:
        pasSalida = Arista(nodo_q2, hilera[-1],peso=2, tipo="pasillo", capacidad=2)
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
                        pasD1 = Arista(desahogo_nodo, hileras[k_index][ubicacion_corte],peso=2, tipo="pasillo", capacidad=2)
                        pasD2 = Arista(desahogo_nodo, hileras[k_index][ubicacion_corte + 1],peso=2, tipo="pasillo", capacidad=2)
                        G.add_edge(desahogo_nodo, hileras[k_index][ubicacion_corte], objeto_arista = pasD1)
                        G.add_edge(desahogo_nodo, hileras[k_index][ubicacion_corte + 1],  objeto_arista = pasD2)
            if j > 0:
                # Se busca el nodo de desahogo anterior para conectarlo
                for node in G.nodes():
                    if isinstance(node, Nodo) and node.nombre == f"d{i}_{j-1}":
                        pasEx = Arista(desahogo_nodo,node, peso=2, tipo="pasillo", capacidad=2)
                        G.add_edge(desahogo_nodo, node, objeto_arista = pasEx)
                        break

    return G


def create_robots(num_robots, graph):
    """
    Crea una lista de robots ubicados en nodos aleatorios del grafo.

    Entradas:
        num_robots (int): Número de robots a crear.
        graph (networkx.Graph): Grafo del almacén.

    Salida:
        robots (list): Lista de objetos Robot con posiciones iniciales aleatorias.
    """
    nodes = list(graph.nodes())
    robots = []
    
    for i in range(num_robots):
        start_node = random.choice(nodes)
        robot = Robot(id=i + 1, position=start_node)
        robots.append(robot)
    
    return robots


def a_star_search(graph, start, goal):
    """Algoritmo A* para hallar el camino de costo mínimo."""
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
                priority = new_cost  # En este ejemplo no se utiliza heurística adicional
                heapq.heappush(queue, (priority, neighbor))
                came_from[neighbor] = current
    
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    return path[::-1]


def simulate_robots(graph, robots, steps, method="A*"):
    """
    Simula el movimiento de los robots en el almacén con asignación de paquetes.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    # Se obtienen las posiciones a partir del atributo de cada objeto Nodo.
    pos = {node: node.posicion for node in graph.nodes()}
    
    # Buscar el nodo de entrada (q1) para simular la generación de paquetes.
    entry_node = None
    for node in graph.nodes():
        if isinstance(node, Nodo) and node.nombre == "q1":
            entry_node = node
            break

    for step in range(steps):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=350, node_color="lightblue")
        
        # Generar "paquetes" en el nodo de entrada (se utiliza una lista como contador)
        packages = [None] * min(len(robots), random.randint(1, len(robots)))
        
        # Asignar un destino aleatorio a cada robot disponible
        for robot in robots:
            if robot.target is None and packages:
                target = random.choice(list(graph.nodes()))
                robot.set_target(target)
                packages.pop()
        
        # Mover robots utilizando el algoritmo A*
        for robot in robots:
            if robot.target:
                path = a_star_search(graph, robot.position, robot.target)
                if len(path) > 1:
                    robot.mover(path[1])
                if robot.position == robot.target:
                    robot.target = None
        
        # Dibujar la posición de los robots
        robot_positions = [robot.position.posicion for robot in robots]
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")
        
        # Construir leyenda con el estado de cada robot
        legend_texts = []
        for robot in robots:
            target_name = robot.target.nombre if robot.target is not None else "Sin destino"
            legend_texts.append(f"Robot {robot.id}: {target_name}")
        legend_texts.append(f"Paso {step + 1}/{steps}")
        ax.legend(handles=[], labels=legend_texts, loc="upper left", fontsize=12, frameon=True)
        
        plt.pause(0.5)

    plt.ioff()
    plt.show()
