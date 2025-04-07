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
        print(f"[RECOGIDA] Robot {robot.id} enviado a q1.")

    def almacenamiento(self, robot, destino):
        robot.set_estado('almacenamiento')
        robot.set_target(destino)
        robot.path = a_star_search(self.graph, robot.position, destino)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        print(f"[ALMACENAMIENTO] Robot {robot.id} enviado al estante {destino.nombre}.")

    def espera(self, robot):
        robot.set_estado('espera')
        robot.set_target(None)
        robot.path = []
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        print(f"[ESPERA] Robot {robot.id} en espera en posición actual.")

    def buscar(self, robot, nodo_paquete):
        robot.set_estado('buscar')
        robot.set_target(nodo_paquete)
        robot.path = a_star_search(self.graph, robot.position, nodo_paquete)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        print(f"[BUSCAR] Robot {robot.id} buscando paquete en {nodo_paquete.nombre}.")

    def salida(self, robot):
        robot.set_estado('salida')
        robot.set_target(self.nodo_q2)
        robot.path = a_star_search(self.graph, robot.position, self.nodo_q2)
        robot.current_edge_index = 0
        robot.progress_along_edge = 0.0
        print(f"[SALIDA] Robot {robot.id} llevando paquete a q2.")

    def asignar_tareas(self, gestor_paquetes):
        for robot in self.robots:
            if robot.estado == 'espera' or robot.target is None:
                # Prioridad máxima: sacar paquetes del almacén (emisión)
                emision = gestor_paquetes.obtener_proximo_emision()
                if emision:
                    paquete, estante_origen = emision
                    robot.paquete_actual = paquete
                    self.buscar(robot, estante_origen)
                    robot.destino_final = self.nodo_q2
                    continue  # Mantener este continue

                # Segunda prioridad: almacenar paquetes entrantes (recepción)
                recepcion = gestor_paquetes.obtener_proximo_recepcion()
                if recepcion:
                    destino = self.estante_mas_libre(recepcion.producto)
                    if destino:
                        robot.paquete_actual = recepcion
                        self.recogida(robot)
                        robot.destino_final = destino
                        continue  # Mantener este continue
                    else:
                        # Este es el cambio clave:
                        # Si no hay destino compatible, devolver paquete a la cola
                        print("[AVISO] No hay estantes compatibles disponibles. Paquete devuelto a cola.")
                        gestor_paquetes.cola_recepcion.insert(0, recepcion)
                        # No usar continue aquí, porque no se asignó tarea al robot aún.

                # Por defecto, espera si no hay tareas
                self.espera(robot)

    # def asignar_tareas(self, gestor_paquetes):
    #     for robot in self.robots:
    #         if robot.estado == 'espera' or robot.target is None:
    #             # Prioridad máxima: sacar paquetes del almacén (emisión)
    #             emision = gestor_paquetes.obtener_proximo_emision()
    #             if emision:
    #                 paquete, estante_origen = emision
    #                 robot.paquete_actual = paquete
    #                 self.buscar(robot, estante_origen)
    #                 robot.destino_final = self.nodo_q2
    #                 continue

    #             # Segunda prioridad: almacenar paquetes entrantes (recepción)
    #             recepcion = gestor_paquetes.obtener_proximo_recepcion()
    #             if recepcion:
    #                 destino = self.estante_mas_libre(recepcion.producto)
    #                 if destino:
    #                     robot.paquete_actual = recepcion
    #                     self.recogida(robot)
    #                     robot.destino_final = destino
    #                 else:
    #                     print("[AVISO] No hay espacio disponible para almacenar el paquete recibido.")
    #                     gestor_paquetes.cola_recepcion.insert(0, recepcion)  # devolver paquete a cola
    #                 continue

    #             # Por defecto, esperar si no hay tareas
    #             self.espera(robot)

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

    # def estante_mas_libre(self, producto):
    #     candidatos = [
    #         node for node in self.graph.nodes 
    #         if node.estante and (
    #             node.almacenamiento is None or 
    #             (node.almacenamiento[0] == producto and node.get_cantidad() < 10)
    #         )
    #     ]
    #     if not candidatos:
    #         return None
    #     return min(candidatos, key=lambda nodo: nodo.get_cantidad())


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
        print(f"[RECEPCIÓN] Nuevo paquete recibido: {paquete.producto}")

    def emision(self, estantes):
        """
        Solicita emitir un paquete que ya esté almacenado en algún estante.
        
        :param estantes: lista de nodos tipo estante del almacén
        """
        # Filtrar estantes que contienen paquetes
        estantes_con_paquetes = [estante for estante in estantes if estante.hay_paquetes()]

        if not estantes_con_paquetes:
            print("[EMISIÓN] No hay paquetes disponibles para emitir.")
            return None

        # Seleccionar un estante aleatorio que tenga paquetes
        estante_elegido = random.choice(estantes_con_paquetes)
        producto, cantidad = estante_elegido.almacenamiento

        # Crear paquete solicitado para emisión
        paquete_solicitado = Paquete(producto=producto)
        self.cola_emision.append((paquete_solicitado, estante_elegido))
        print(f"[EMISIÓN] Solicitado paquete '{producto}' desde estante {estante_elegido.nombre}")

    def obtener_proximo_recepcion(self):
        if self.cola_recepcion:
            return self.cola_recepcion.pop(0)
        return None

    def obtener_proximo_emision(self):
        if self.cola_emision:
            return self.cola_emision.pop(0)
        return None
