from algoritmos import a_star_search
from Clases import Paquete
import random

class GestionRobots:
    def __init__(self, robots, nodo_q1, nodo_q2, graph):
        self.robots = robots
        self.nodo_q1 = nodo_q1
        self.nodo_q2 = nodo_q2
        self.graph = graph

    def recogida(self, robot):
        robot.set_estado('recogida')
        robot.set_target(self.nodo_q1)
        robot.path = a_star_search(self.graph, robot.position, robot.target)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[RECOGIDA] Robot {robot.id} enviado a q1.")

    def almacenamiento(self, robot, destino):
        robot.set_estado('almacenamiento')
        robot.set_target(destino)
        robot.path = a_star_search(self.graph, robot.position, destino)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[ALMACENAMIENTO] Robot {robot.id} enviado al estante {destino.nombre}.")

    def espera(self, robot):
        robot.set_estado('espera')
        robot.set_target(None)
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[ESPERA] Robot {robot.id} en espera en posición actual.")

    def buscar(self, robot, nodo_paquete):
        robot.set_estado('buscar')
        robot.set_target(nodo_paquete)
        robot.path = a_star_search(self.graph, robot.position, nodo_paquete)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        # print(f"[BUSCAR] Robot {robot.id} buscando paquete en {nodo_paquete.nombre}.")

    def salida(self, robot):
        robot.set_estado('salida')
        robot.set_target(self.nodo_q2)
        robot.path = a_star_search(self.graph, robot.position, self.nodo_q2)
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


    def reasignacion(self, robot, gestor_paquetes, paquetes_visuales):
        """
        Tras fallar al almacenar un paquete (producto distinto o estante lleno),
        este método busca un estante alternativo. 
        Si no hay ninguno, el paquete se devuelve a la cola de recepción.
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

        # Preparamos el robot para ir al nuevo objetivo
        robot.target = destino_alternativo
        # Recalculamos la ruta al estante alternativo con A*
        from algoritmos import a_star_search
        robot.path = a_star_search(self.graph, robot.position, destino_alternativo)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0

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
        paquete = Paquete(producto=producto)
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
        paquete_solicitado = Paquete(producto=producto)
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
