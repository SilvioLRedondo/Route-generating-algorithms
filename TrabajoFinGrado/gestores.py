from algoritmos import a_star_search, a_star_with_reservations
from Clases import Paquete, Actividad, NivelBateria
import random
from const import THRESHOLD_HIGH,THRESHOLD_LOW

class GestionRobots:
    def __init__(self, robots, nodo_q1, nodo_q2, graph, hilera_reservations):
        self.robots = robots
        self.nodo_q1 = nodo_q1
        self.nodo_q2 = nodo_q2
        self.graph = graph
        self.hilera_reservations = hilera_reservations
        self.estaciones = [n for n in graph.nodes if getattr(n, 'estacion', False)]

    def plan_route(
        self,
        robot,
        current_time,
        edge_reservations,
        hilera_reservations,
        obstacles=None,
        max_hilera_h=None,
        metrics = None
    ):
        """Plan and reserve a route for the robot using time aware A*."""

        if metrics is not None and current_time > 0:
            metrics["replanifications"] += 1

        if robot.target is None:
            return False
        # 1) Release old reservations for this robot
        edge_reservations.release_robot(robot.id)
        # 2) Plan a new route
        path, times = a_star_with_reservations(
            self.graph,
            robot.position,
            robot.target,
            current_time,
            edge_reservations,
            hilera_reservations,
            robot.prioridad,
            obstacles,
            max_hilera_h,
        )
        if path:
            robot.path = path
            robot.edge_times = times
            robot.current_edge_index = 0
            robot.progress_along_edge = 0.0
            if edge_reservations.reserve_path(robot.id, path, current_time, self.graph):
                times_nodes = [current_time] + times
                for node, t in zip(path, times_nodes):
                    hilera_reservations.reserve(int(node.posicion[0]), t, robot.id, robot.prioridad)
                return True
            robot.path = []
            robot.edge_times = []
            robot.current_edge_index = 0
            robot.progress_along_edge = 0.0
            return False
        robot.path = []
        robot.edge_times = []
        return False

    def recogida(self, robot):
        robot.set_actividad(Actividad.RECOGIDA.value)
        robot.set_target(self.nodo_q1)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def almacenamiento(self, robot, destino):
        robot.set_actividad(Actividad.ALMACENAMIENTO.value)
        robot.set_target(destino)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def espera(self, robot):
        robot.set_actividad(Actividad.ESPERA.value)
        robot.set_target(None)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        robot.recharge_pending = False

    def buscar(self, robot, nodo_paquete):
        robot.set_actividad(Actividad.BUSCAR.value)
        robot.set_target(nodo_paquete)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def salida(self, robot):
        robot.set_actividad(Actividad.SALIDA.value)
        robot.set_target(self.nodo_q2)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

    def asignar_tareas(self, gestor_paquetes):
        """
        Asigna tareas a los robots dependiendo de si el almacén está 
        por debajo o por encima del 70% de ocupación.
        """
        # 1) Calcular la ocupación actual
        ocupacion = self.calcular_indice_almacenamiento()
        

        for robot in self.robots:
            if robot.nivel_bateria != NivelBateria.OPERATIVO.value:
                continue
            # Atendemos solo robots disponibles (actividad 'espera' o sin target)
            if robot.actividad == Actividad.ESPERA.value or robot.target is None:

                if ocupacion < THRESHOLD_LOW:
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

                elif ocupacion >= THRESHOLD_HIGH:
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
                            
                else:
                    num_rec = len(gestor_paquetes.cola_recepcion)
                    num_emi = len(gestor_paquetes.cola_emision)
                    # Si las colas empatan o la de recepción es mayor, priorizamos RECEPCIÓN
                    if num_rec >= num_emi:
                        recepcion = gestor_paquetes.obtener_proximo_recepcion()
                        if recepcion:
                            destino = self.estante_mas_libre(recepcion.producto)
                            if destino:
                                robot.paquete_actual = recepcion
                                self.recogida(robot)
                                robot.destino_final = destino
                                continue
                    # En caso contrario priorizamos EMISIÓN
                    emision = gestor_paquetes.obtener_proximo_emision()
                    if emision:
                        paquete, estante_origen = emision
                        robot.paquete_actual = paquete
                        self.buscar(robot, estante_origen)
                        robot.destino_final = self.nodo_q2
                        continue
                    # Si no hay nada pendiente, espera
                    self.espera(robot)
                    continue                    


    def nearest_station(self, position, obstacles=None):
        return min(self.estaciones, key=lambda s: len(a_star_search(self.graph, position, s, obstacles)))

    def puede_completar_tarea(self, robot, obstacles=None):
        if robot.target is None:
            return True
        path = a_star_search(self.graph, robot.position, robot.target, obstacles)
        dist = len(path) - 1
        if robot.destino_final and robot.destino_final != robot.target:
            path2 = a_star_search(self.graph, robot.target, robot.destino_final, obstacles)
            dist += len(path2) - 1
        return robot.autonomia >= dist

    def enviar_a_estacion(self, robot, station):
        robot.set_nivel_bateria(NivelBateria.CRITICO.value)
        robot.pausar_tarea()
        robot.set_target(station)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.recharge_pending = False

    def iniciar_recarga(self, robot):
        robot.set_actividad(Actividad.RECARGA.value)
        robot.path = []
        robot.edge_times = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        robot.recharge_pending = False

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
        Devuelve la fracción de estantes ocupados (≥ 1 paquete) sobre el total.
        Valor 0.0 = almacén vacío, 1.0 = todos los estantes con algo.
        """
        estantes = [n for n in self.graph.nodes if n.estante]
        if not estantes:
            return 0.0
        ocupados = sum(1 for e in estantes if e.hay_paquetes())
        return ocupados / len(estantes)


    def reasignacion(
        self,
        robot,
        gestor_paquetes,
        paquetes_visuales,
        current_time,
        edge_reservations,
        hilera_reservations,
        obstacles=None,
        max_hilera_h=None,
        metrics = None
    ):
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
            robot.set_actividad(Actividad.ESPERA.value)

            return  # fin de reasignacion


        # Preparamos el robot para ir al nuevo objetivo y calcular su ruta
        # Utilizamos plan_route para reservar la ruta con conocimiento temporal
        # evitando así que se generen "edge_times" vacíos.
        robot.target = destino_alternativo
        self.plan_route(
            robot,
            current_time,
            edge_reservations,
            hilera_reservations,
            obstacles,
            max_hilera_h,
            metrics,
        )

        # Mantenemos o reestablecemos el robot en estado 'almacenamiento' para que
        # cuando llegue al destino, vuelva a ejecutar el mismo bloque de "almacenamiento"
        robot.set_actividad(Actividad.ALMACENAMIENTO.value)



class GestionPaquetes:
    def __init__(self):
        self.cola_recepcion = []  # Paquetes que llegan a q1
        self.cola_emision = []    # Paquetes solicitados para salir por q2

    def recepcion(self, current_time):
        """
        Genera un paquete aleatorio para recepción en q1.
        """
        producto = random.choice(Paquete.productos_disponibles)
        paquete = Paquete(producto=producto, peso=random.uniform(1, 10))
        paquete.created_at = current_time
        self.cola_recepcion.append(paquete)

    def emision(self, estantes):
        """
        Solicita emitir un paquete que ya esté almacenado en algún estante.
        
        :param estantes: lista de nodos tipo estante del almacén
        """
        # Filtrar estantes que contienen paquetes
        estantes_con_paquetes = [estante for estante in estantes if estante.hay_paquetes()]

        if not estantes_con_paquetes:
            return None

        # Seleccionar un estante aleatorio que tenga paquetes
        estante_elegido = random.choice(estantes_con_paquetes)
        producto, cantidad = estante_elegido.almacenamiento

        # Crear paquete solicitado para emisión
        paquete_solicitado = Paquete(producto=producto, peso=random.uniform(1, 10))
        self.cola_emision.append((paquete_solicitado, estante_elegido))

    def obtener_proximo_recepcion(self):
        if self.cola_recepcion:
            return self.cola_recepcion.pop(0)
        return None

    def obtener_proximo_emision(self):
        if self.cola_emision:
            return self.cola_emision.pop(0)
        return None
