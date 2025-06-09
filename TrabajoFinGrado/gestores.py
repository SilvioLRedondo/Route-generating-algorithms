from algoritmos import a_star_search, a_star_with_reservations
from Clases import Paquete
import random

class GestionRobots:
    def __init__(self, robots, nodo_q1, nodo_q2, graph):
        self.robots = robots
        self.nodo_q1 = nodo_q1
        self.nodo_q2 = nodo_q2
        self.graph = graph
        self.estaciones = [n for n in graph.nodes if getattr(n, 'estacion', False)]

    def plan_route(self, robot, current_time, reservations, obstacles=None):
        """Plan and reserve a route for the robot using time aware A*."""
        if robot.target is None:
            return False
        path, times = a_star_with_reservations(self.graph, robot.position, robot.target, current_time, reservations, obstacles)
        if path:
            robot.path = path
            robot.edge_times = times
            robot.current_edge_index = 0
            robot.progress_along_edge = 0.0
            reservations.reserve_path(robot.id, path, current_time)
            return True
        robot.path = []
        robot.edge_times = []
        return False

    def recogida(self, robot):
        robot.set_estado('recogida')
        robot.set_target(self.nodo_q1)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[RECOGIDA] Robot {robot.id} enviado a q1.")

    def almacenamiento(self, robot, destino):
        robot.set_estado('almacenamiento')
        robot.set_target(destino)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[ALMACENAMIENTO] Robot {robot.id} enviado al estante {destino.nombre}.")

    def espera(self, robot):
        robot.set_estado('espera')
        robot.set_target(None)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[ESPERA] Robot {robot.id} en espera en posición actual.")

    def buscar(self, robot, nodo_paquete):
        robot.set_estado('buscar')
        robot.set_target(nodo_paquete)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[BUSCAR] Robot {robot.id} buscando paquete en {nodo_paquete.nombre}.")

    def salida(self, robot):
        robot.set_estado('salida')
        robot.set_target(self.nodo_q2)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[SALIDA] Robot {robot.id} llevando paquete a q2.")

    def asignar_tareas(self, gestor_paquetes):
        """
        Asigna tareas a los robots dependiendo de si el almacén está 
        por debajo o por encima del 70% de ocupación.
        """
        # 1) Calcular la ocupación actual
        ocupacion = self.calcular_indice_almacenamiento()
        umbral = 0.7

        for robot in self.robots:
            # Atendemos solo robots disponibles (estado 'espera' o sin target)
            if robot.estado == 'espera' or robot.target is None:

                if ocupacion < umbral:
                    # ------------------------------------------
                    # PRIORIDAD: RECEPCIÓN
                    # ------------------------------------------
                    recepcion = gestor_paquetes.obtener_proximo_recepcion()
                    if recepcion:
                        # Buscar estante más libre para ese producto
                        destino = self.estante_mas_libre(recepcion.producto)
                        if destino:
                            # Asignamos paquete al robot y le mandamos a q1 (recogida), 
                            # después hará almacenamiento
                            robot.paquete_actual = recepcion
                            self.recogida(robot)  
                            robot.destino_final = destino
                            continue
                        else:
                            # No hay estante compatible => devolvemos a la cola
                            # y el robot queda en espera
                            gestor_paquetes.cola_recepcion.insert(0, recepcion)
                            self.espera(robot)
                            continue
                    else:
                        # Si NO hay paquetes de recepción => ver si hay emisión
                        emision = gestor_paquetes.obtener_proximo_emision()
                        if emision:
                            paquete, estante_origen = emision
                            robot.paquete_actual = paquete
                            self.buscar(robot, estante_origen)
                            robot.destino_final = self.nodo_q2
                            continue
                        else:
                            # Ni recepción ni emisión => robot a espera
                            self.espera(robot)
                            continue

                else:
                    # ------------------------------------------
                    # PRIORIDAD: EMISIÓN
                    # ------------------------------------------
                    emision = gestor_paquetes.obtener_proximo_emision()
                    if emision:
                        paquete, estante_origen = emision
                        robot.paquete_actual = paquete
                        self.buscar(robot, estante_origen)
                        robot.destino_final = self.nodo_q2
                        continue
                    else:
                        # Si no hay emisión => probamos recepción
                        recepcion = gestor_paquetes.obtener_proximo_recepcion()
                        if recepcion:
                            destino = self.estante_mas_libre(recepcion.producto)
                            if destino:
                                robot.paquete_actual = recepcion
                                self.recogida(robot)
                                robot.destino_final = destino
                                continue
                            else:
                                # Sin estantes compatibles, paquete a cola y robot en espera
                                gestor_paquetes.cola_recepcion.insert(0, recepcion)
                                self.espera(robot)
                                continue
                        else:
                            # Ni emisión ni recepción => espera
                            self.espera(robot)
                            continue


    def nearest_station(self, position, obstacles=None):
        return min(self.estaciones, key=lambda s: len(a_star_search(self.graph, position, s, obstacles)))

    def puede_completar_tarea(self, robot, obstacles=None):
        if robot.target is None:
            return True

        if obstacles is None:
            obstacles = set()

        # ----- calculate remaining distance from current position to task target
        path = a_star_search(self.graph, robot.position, robot.target, obstacles)
        if not path:
            return False

        total_distance = 0.0
        edge_count = 0

        for i in range(len(path) - 1):
            edge = self.graph[path[i]][path[i + 1]]["objeto_arista"]
            length = edge.longitud()
            # subtract progress already made on the first edge
            if i == 0 and robot.progress_along_edge > 0:
                length = max(0.0, length - robot.progress_along_edge)
            total_distance += length
            edge_count += 1

        # ----- if there is a final destination after the task, add that segment
        if robot.destino_final and robot.destino_final != robot.target:
            path2 = a_star_search(self.graph, robot.target, robot.destino_final, obstacles)
            if not path2:
                return False
            for i in range(len(path2) - 1):
                edge = self.graph[path2[i]][path2[i + 1]]["objeto_arista"]
                total_distance += edge.longitud()
                edge_count += 1

        payload_weight = robot.paquete_actual.peso if robot.paquete_actual else 0
        # energy = distance + cost per edge based on payload weight
        required_energy = total_distance + (edge_count * payload_weight * 0.1)

        return robot.autonomia >= required_energy

    def enviar_a_estacion(self, robot, station):
        robot.set_estado('critico')
        robot.set_target(station)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def iniciar_recarga(self, robot):
        robot.set_estado('recargando')
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def estante_mas_libre(self, producto):
        candidatos = [
            node for node in self.graph.nodes 
            if node.estante and (
                node.almacenamiento is None or 
                (node.almacenamiento[0] == producto and node.get_cantidad() < 10)
            )
        ]
        if not candidatos:
            return None

        # Prioridad estantes ya con mismo producto, luego vacíos
        estantes_mismo_producto = [
            estante for estante in candidatos 
            if estante.almacenamiento and estante.almacenamiento[0] == producto
        ]

        if estantes_mismo_producto:
            return min(estantes_mismo_producto, key=lambda nodo: nodo.get_cantidad())

        # Si no hay estantes con el mismo producto, usa uno vacío
        estantes_vacios = [estante for estante in candidatos if estante.almacenamiento is None]
        if estantes_vacios:
            return random.choice(estantes_vacios)

        return None
    
    
    def calcular_indice_almacenamiento(self):
        """
        Calcula la fracción de ocupación global del almacén.
        Devuelve un valor entre 0.0 (vacío) y 1.0 (completamente lleno).
        """
        # 1) Listar todos los nodos que sean estantes
        estantes = [node for node in self.graph.nodes if node.estante is not None]
        if not estantes:
            return 0.0  # No hay estantes => índice 0

        # 2) Capacidad total = cantidad de estantes * 10 (pues cada uno admite hasta 10 paquetes)
        capacidad_total = len(estantes) * 10

        # 3) Sumar cuántos paquetes hay ocupados realmente
        paquetes_almacenados = 0
        for estante in estantes:
            if estante.almacenamiento is not None:
                paquetes_almacenados += estante.almacenamiento[1]  # la segunda parte de la tupla (producto, cantidad)

        # 4) Calcular índice = paquetes_almacenados / capacidad_total
        return paquetes_almacenados / capacidad_total


    def reasignacion(self, robot, gestor_paquetes, paquetes_visuales, current_time, reservations, obstacles=None):
        """Reasigna el objetivo de ``robot`` a otro estante disponible.

        ``current_time`` indica el instante actual y ``reservations`` gestiona las
        reservas de aristas. Se utiliza una planificación con tiempo para evitar
        problemas de rutas sin ``edge_times`` cuando el robot cambia de destino.
        """
        # 1) Identificamos el producto que lleva el robot
        producto = robot.paquete_actual.producto

        # 2) Reutilizamos la lógica que ya tenemos en 'estante_mas_libre' para hallar un estante adecuado.
        #    'estante_mas_libre' devuelve None si no hay estantes con hueco para el producto.
        destino_alternativo = self.estante_mas_libre(producto)

        # 3) Si no existe estante que admita el producto, devolvemos el paquete a la cola
        if not destino_alternativo:
            print("[REASIGNACIÓN] No se encontró un estante libre/compatible. Devolviendo paquete a cola.")
            # Devolver el paquete a cola_recepcion para reintentar más tarde
            gestor_paquetes.cola_recepcion.append(robot.paquete_actual)
            
            # Quitar el paquete del robot y de la visual
            paquetes_visuales.remove(robot.paquete_actual)
            robot.paquete_actual = None

            # Poner al robot en espera (sin objetivo)
            robot.target = None
            robot.path = []
            robot.current_edge_index = 0
            robot.progress_along_edge = 0.0
            robot.set_estado('espera')

            return  # fin de reasignacion

        # 4) Si encontramos un estante alternativo, reasignamos el robot a ese nuevo destino
        # print(f"[REASIGNACIÓN] Se reasigna el robot {robot.id} al estante '{destino_alternativo.nombre}'.")

        # Preparamos el robot para ir al nuevo objetivo y calcular su ruta
        # Utilizamos plan_route para reservar la ruta con conocimiento temporal
        # evitando así que se generen "edge_times" vacíos.
        robot.target = destino_alternativo
        self.plan_route(robot, current_time, reservations, obstacles)

        # Mantenemos o reestablecemos el robot en estado 'almacenamiento' para que
        # cuando llegue al destino, vuelva a ejecutar el mismo bloque de "almacenamiento"
        robot.set_estado('almacenamiento')



class GestionPaquetes:
    def __init__(self):
        self.cola_recepcion = []  # Paquetes que llegan a q1
        self.cola_emision = []    # Paquetes solicitados para salir por q2

    def recepcion(self):
        """
        Genera un paquete aleatorio para recepción en q1.
        """
        producto = random.choice(Paquete.productos_disponibles)
        paquete = Paquete(producto=producto, peso=random.uniform(1, 10))
        self.cola_recepcion.append(paquete)
        # print(f"[RECEPCIÓN] Nuevo paquete recibido: {paquete.producto}")

    def emision(self, estantes):
        """
        Solicita emitir un paquete que ya esté almacenado en algún estante.
        
        :param estantes: lista de nodos tipo estante del almacén
        """
        # Filtrar estantes que contienen paquetes
        estantes_con_paquetes = [estante for estante in estantes if estante.hay_paquetes()]

        if not estantes_con_paquetes:
            # print("[EMISIÓN] No hay paquetes disponibles para emitir.")
            return None

        # Seleccionar un estante aleatorio que tenga paquetes
        estante_elegido = random.choice(estantes_con_paquetes)
        producto, cantidad = estante_elegido.almacenamiento

        # Crear paquete solicitado para emisión
        paquete_solicitado = Paquete(producto=producto, peso=random.uniform(1, 10))
        self.cola_emision.append((paquete_solicitado, estante_elegido))
        # print(f"[EMISIÓN] Solicitado paquete '{producto}' desde estante {estante_elegido.nombre}")

    def obtener_proximo_recepcion(self):
        if self.cola_recepcion:
            return self.cola_recepcion.pop(0)
        return None

    def obtener_proximo_emision(self):
        if self.cola_emision:
            return self.cola_emision.pop(0)
        return None
