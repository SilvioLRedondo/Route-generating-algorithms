
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
            




