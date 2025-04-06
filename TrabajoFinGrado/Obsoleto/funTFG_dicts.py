# Este es el módulo antiguo utilizado para la creación y simulación de objetos que tienen por objeto resolver 
# el VRP en un almacén robotizado, finalmente se descarta su uso dada la eficiencia de los nodos cómo clases.
# Este archivo sobrevive con fines didácticos.

# Para ejecutar, copiar en un archivo main y descomentar las siguientes lineas:
# -----------
# import networkx as nx
# import matplotlib.pyplot as plt
# import funTFG_dicts
# if __name__ == "__main__":
#     n, m, k, d = 3, 8, 24, 1  # Parámetros del almacén  
#     num_robots = 3  # Número de robots
#     steps = 10 # Pasos de la simulación
#     graph = funTFG_dicts.GraphGen(n, m, k, d)
#     posEstante = nx.get_node_attributes(graph, 'posicion')
#     Estantes = nx.get_node_attributes(graph,'Estante')
#     robots = funTFG_dicts.create_robots(num_robots, graph)
#     funTFG_dicts.simulate_robots(graph, robots, steps)
#------------------



import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq

def GraphGen(n, m, k, d):
    """
    Crea un grafo que representa un almacén con dimensiones n x m, k ubicaciones de almacenamiento
    y tantos pasillos de desahogo cómo indique d

    Entradas:
        n (int): Número de hileras (ancho del almacén).
        m (int): Largo del almacén (número máximo de ubicaciones por hilera).
        k (int): Número total de ubicaciones de almacenamiento. No puede ser superior a n*m.
        d (int): Número de pasillos de desahogo. Debe ser un enterno menor que el mayor divisor de m.

    Salida:
        G (networkx.Graph): Grafo generado.
    """

    if k > n * m:
        raise ValueError("El número de ubicaciones k no puede exceder el espacio total disponible n * m.")
    if d >= (k // n) + (1 if k % n > 0 else 0):
        raise ValueError("El desahogo debe estar dentro de la cantidad de ubicaciones por hilera.")

    medio = (n-1)/2
    print('impar')
    if n%2 ==0:
        print('par')
        medio = n/2 -0.5
    
    G = nx.Graph()
    
    # Nodos de entrada y salida
    G.add_node("q1",peso=1, altura = 2, posicion = (medio,-1))  # Entrada
    G.add_node("q2",peso=1, altura = 2, posicion = (medio,m))  # Salida

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
            G.add_node(nodo, posicion = (i,j),Estante = {'posEstante':(i,j),'producto':'nada','Completo':False})
            hilera.append(nodo)
            nodo_id += 1
        hileras.append(hilera)

    # Conectar nodos dentro de las hileras
    for hilera in hileras:
        for i in range(len(hilera) - 1):
            G.add_edge(hilera[i], hilera[i + 1],weight=1)

    # Conexión entre extremos de las hileras
    for i in range(len(hileras) - 1):
        G.add_edge(hileras[i][0], hileras[i + 1][0],weight=1)  # Entrada de hilera i con i+1
        G.add_edge(hileras[i][-1], hileras[i + 1][-1],weight=1)  # Salida de hilera i con i+1
    
    # Conectar entrada del almacén con las primeras ubicaciones de cada hilera
    for hilera in hileras:
        G.add_edge("q1", hilera[0],weight=1, a= 2)

    # Conectar salida del almacén con las últimas ubicaciones de cada hilera
    for hilera in hileras:
        G.add_edge("q2", hilera[-1],weight=1)
    
    # Creación de pasillos. esto lo dejo por si fuera de utilidad, actualmente
    # todo esto se hace en el siguiente bucle, esto es útil para visualizar 
    # los pasillos

    #ubicaciones_corte=[]
    #for i in range(d):
    #    a = (m//(d+1))*(i+1)
    #    ubicaciones_corte.append(a)
    #print(ubicaciones_corte)


    # Conectar nodos adyacentes en la columna del desahogo
  
    for i in range(d):#range(len(hileras)):
        #if d < m:#len(hileras[i]):
        for j in range(n-1):
            desahogo_nodo = f"d{i}_{j}"
            G.add_node(desahogo_nodo,peso=1, altura = 2, posicion = (j+0.5,(m/(d+1))*(i+1) -0.5 ))
            ubicacion_corte = (m//(d+1))*(i+1) -1
            for k in range(j,j+2):
                G.add_edge(desahogo_nodo, hileras[k][ubicacion_corte], weight=1.5)
                G.add_edge(desahogo_nodo, hileras[k][ubicacion_corte+1], weight=1.5)
                if j > 0:
                     G.add_edge(desahogo_nodo, f"d{i}_{j-1}", weight=1.5)
                
    
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
        robot = {"id": i+1, "position": start_node, "target": None, "distance":0, "Capacidad de carga":0, "autonomía":100, "disponible":True} 
        # La autonomía del robot se presenta cómo un porcentaje, puede tratarse de minutos de actividad, distancia recorrida...
        # La capacidad de carga debería ser en peso, no en número de paquetes.*
        robots.append(robot)
    
    return robots

def a_star_search(graph, start, goal):
    """Algoritmo A*"""
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while queue:
        _, current = heapq.heappop(queue)
        
        if current == goal:
            break
        
        for neighbor in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph[current][neighbor]['weight']
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost ##
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
    pos = nx.get_node_attributes(graph, 'posicion')
    
    for step in range(steps):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=350, node_color="lightblue")
        
        # Generar paquetes en q1
        packages = ["q1"] * min(len(robots), random.randint(1, len(robots)))

        # Asignar paquetes a robots disponibles
        for robot in robots:
            if robot["target"] is None and packages:
                target = random.choice(list(graph.nodes))  # Ubicación aleatoria
                robot["target"] = target
                packages.pop()

        # Mover robots siguiendo A*
        for robot in robots:
            if robot["target"]:
                path = a_star_search(graph, robot["position"], robot["target"])
                if len(path) > 1:
                    robot["position"] = path[1]
                if robot["position"] == robot["target"]:
                    robot["target"] = None
        
        # Dibujar robots
        robot_positions = [pos[robot["position"]] for robot in robots]
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")
        
        # Construir leyenda con ID de robots y targets
        legend_texts = [f"Robot {i}: {robot['target'] if robot['target'] else 'Sin destino'}" 
                        for i, robot in enumerate(robots)]
        legend_texts.append(f"Paso {step + 1}/{steps}")
        ax.legend(handles=[], labels=legend_texts, loc="upper left", fontsize=12, frameon=True)
        
        plt.pause(0.5)

    plt.ioff()
    plt.show()

def simulate_robots1(graph, robots, steps, method="A*"):
    """
    Simula el movimiento de los robots en el almacén con asignación de paquetes.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = nx.get_node_attributes(graph, 'posicion')

    for step in range(steps):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=350, node_color="lightblue")

        # Generar paquetes en q1
        packages = ["q1"] * min(len(robots), random.randint(1, len(robots)))

        # Asignar paquetes a robots disponibles
        for robot in robots:
            if robot["target"] is None and packages:
                target = random.choice(list(graph.nodes))
                robot["target"] = target
                packages.pop()

        # Mover robots
        for robot in robots:
            if robot["target"]:
                path = a_star_search(graph, robot["position"], robot["target"])
                if len(path) > 1:
                    robot["position"] = path[1]
                if robot["position"] == robot["target"]:
                    robot["target"] = None

        # Dibujar robots (sin label general)
        robot_positions = [pos[robot["position"]] for robot in robots]
        ax.scatter(*zip(*robot_positions), color="red", s=750)

        # Crear leyenda dinámica
        legend_labels = [
            f"Robot {robot['id']}: Objetivo {robot['target']}" 
            if robot['target'] 
            else f"Robot {robot['id']}: Sin objetivo" 
            for robot in robots
        ]
        
        # Crear handles para la leyenda (círculos rojos)
        legend_handles = [
            plt.Line2D([0], [0], 
                      marker='o', 
                      color='w',
                      markerfacecolor='red',
                      markersize=10) 
            for _ in robots
        ]
        
        # Añadir leyenda con título del paso
        ax.legend(legend_handles,
                legend_labels,
                title=f"Paso: {step+1}/{steps}",
                loc='upper right',
                bbox_to_anchor=(1.3, 1))  # Ajustar posición si es necesario

        plt.pause(0.5)

    plt.ioff()
    plt.show()

def simulate_robots2(graph, robots, steps, method="A*"):
    """
    Simula el movimiento de los robots en el almacén con asignación de paquetes.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 12))
    pos = nx.get_node_attributes(graph, 'posicion')
    # pos = nx.spring_layout(graph, seed=42)

    for step in range(steps):
        ax.clear()
        nx.draw(graph, pos, with_labels=True, node_size=350, node_color="lightblue")

        # Generar paquetes en q1
        packages = ["q1"] * min(len(robots), random.randint(1, len(robots)))

        # Asignar paquetes a robots disponibles
        for robot in robots:
            if robot["target"] is None and packages:
                target = random.choice(list(graph.nodes))  # Ubicación aleatoria
                robot["target"] = target
                packages.pop()

        # Mover robots siguiendo A*
        for robot in robots:
            if robot["target"]:
                path = a_star_search(graph, robot["position"], robot["target"])
                if len(path) > 1:
                    robot["position"] = path[1]
                if robot["position"] == robot["target"]:
                    robot["target"] = None
        

        # Dibujar robots
        robot_positions = [pos[robot["position"]] for robot in robots]
        ax.scatter(*zip(*robot_positions), color="red", s=750, label="Robots")
        plt.legend()
        plt.pause(0.5)

    plt.ioff()
    plt.show()