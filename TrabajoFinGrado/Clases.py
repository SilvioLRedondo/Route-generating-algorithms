class Nodo:
    def __init__(self, nombre, posicion, peso=None, altura=None, estante=None):
        """
        Constructor del nodo.
        """
        self.nombre = nombre
        self.posicion = posicion
        self.peso = peso # Capacidad
        self.altura = altura
        self.estante = estante # Objeto que contenga

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
        """
        Constructor del robot.
        """
        self.id = id
        self.position = position  # Nodo discreto
        self.target = None
        self.distance = 0
        self.capacidad_carga = 0
        self.autonomia = 100
        self.disponible = True
        # Atributos para la simulación continua:
        self.continuous_position = None  # Posición continua (tuple)
        self.path = []  # Trayectoria (lista de nodos)
        self.current_edge_index = 0  # Índice del segmento actual
        self.progress_along_edge = 0.0  # Progreso (distancia recorrida en el segmento actual)

    def set_target(self, target):
        self.target = target

    def mover(self, nueva_posicion):
        self.position = nueva_posicion

    def __repr__(self):
        return f"Robot {self.id}"

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

    def __init__(self, producto=None):
        """
        Constructor de la clase Paquete.
        Añadir peso.
        
        :param producto: El producto que contiene el paquete. Si no se especifica,
                        se establece como "Otro" por defecto.
        """
        if producto is None:
            self.producto = "Otro"
        else:
            self.producto = producto

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
            