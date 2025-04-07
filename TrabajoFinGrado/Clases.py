import random

class Nodo:
    def __init__(self, nombre, posicion, peso=None, altura=None, estante=None):
        self.nombre = nombre
        self.posicion = posicion
        self.peso = peso
        self.altura = altura
        self.estante = estante
        self.almacenamiento = None  # (producto, cantidad)

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return isinstance(other, Nodo) and self.nombre == other.nombre

    def __repr__(self):
        return self.nombre

    def __lt__(self, other):
        return self.nombre < other.nombre

    def get_posicion(self):
        return self.posicion

    def get_estante(self):
        return self.estante
    
    def esta_lleno(self):
        return self.almacenamiento is not None and self.almacenamiento[1] >= 10

    def esta_vacio(self):
        return self.almacenamiento is None or self.almacenamiento[1] == 0
    
    def añadir_paquete(self, paquete):
        if self.almacenamiento is None:
            self.almacenamiento = (paquete.producto, 1)
        else:
            producto, cantidad = self.almacenamiento
            if producto == paquete.producto:
                if cantidad < 10:
                    self.almacenamiento = (producto, cantidad + 1)
                else:
                    raise ValueError("El estante ya tiene la cantidad máxima de productos (10).")
            else:
                    raise ValueError("No se pueden mezclar productos en el mismo estante.")

    def retirar_paquete(self):
        if self.almacenamiento is None:
            return None
        producto, cantidad = self.almacenamiento
        if cantidad == 1:
            self.almacenamiento = None
        else:
            self.almacenamiento = (producto, cantidad - 1)
        return Paquete(producto)
        return self.almacenamiento is not None and self.almacenamiento[1] >= 10

    def esta_vacio(self):
        return self.almacenamiento is None or self.almacenamiento[1] == 0

    def hay_paquetes(self):
        return self.almacenamiento is not None

    def get_cantidad(self):
        if self.almacenamiento:
            return self.almacenamiento[1]
        return 0



class Arista:
    def __init__(self, nodo1, nodo2, peso=1, tipo="normal", capacidad=1, bidireccional=True):
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso # ocupación
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
        return ((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)**0.5


class Robot:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.target = None
        self.distance = 0
        self.capacidad_carga = 0
        self.autonomia = 100
        self.estado = 'espera'  # recogida, almacenamiento, espera, buscar, salida
        # self.disponible = True
        self.continuous_position = None
        self.path = []
        self.current_edge_index = 0
        self.progress_along_edge = 0.0
        self.paquete_actual = None

    def set_target(self, target):
        self.target = target

    def mover(self, nueva_posicion):
        self.position = nueva_posicion

    def coger_paquete(self, paquete):
        if self.paquete_actual is None:
            self.paquete_actual = paquete
        else:
            raise Exception("El robot ya transporta un paquete.")

    def entregar_paquete(self):
        paquete = self.paquete_actual
        self.paquete_actual = None
        return paquete

    def tiene_paquete(self):
        return self.paquete_actual is not None

    def __repr__(self):
        return f"Robot {self.id}"
    
    def set_estado(self, nuevo_estado):
        estados_validos = ['recogida', 'almacenamiento', 'espera', 'buscar', 'salida']
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
        else:
            raise ValueError(f"Estado '{nuevo_estado}' no válido. Usa {estados_validos}.")


class Paquete:
    # Lista de posibles productos predefinidos
    productos_disponibles = [
        "Libro",
        "Electrónico",
        "Ropa",
        "Juguete",
        "Alimento",
        "Cosmético",
        "Herramienta",
        "Deporte",
        "Mueble",
        "Otro"
    ]

    def __init__(self, producto=None, posicion=None):
        self.producto = producto if producto else "Otro"
        self.posicion = posicion


    @property
    def producto(self):
        """Getter para el atributo producto."""
        return self._producto

    @producto.setter
    def producto(self, valor):
        """
        Setter para el atributo producto.
        Verifica que el producto esté en la lista de productos disponibles.
        Si no está, lanza un ValueError.
        """
        if valor in self.productos_disponibles:
            self._producto = valor
        else:
            raise ValueError(f"Producto no válido. Los productos disponibles son: {', '.join(self.productos_disponibles)}")

    def __str__(self):
        """Representación en string del paquete."""
        return f"Paquete que contiene: {self.producto}"

    @classmethod
    def mostrar_productos_disponibles(cls):
        """Muestra la lista de productos disponibles."""
        print("Productos disponibles:")
        for producto in cls.productos_disponibles:
            print(f"- {producto}")
            


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


from funTFG import a_star_search

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
