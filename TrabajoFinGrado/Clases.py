import random
from enum import Enum


class Actividad(Enum):
    RECOGIDA = "recogida"
    ALMACENAMIENTO = "almacenamiento"
    ESPERA = "espera"
    BUSCAR = "buscar"
    SALIDA = "salida"
    RECARGA = "recarga"
    DIRIGIENDOSE_A_RS = "dirigiendose_a_rs"


class NivelBateria(Enum):
    OPERATIVO = "operativo"
    LIMITADO = "limitado"
    CRITICO = "critico"
    AGOTADO = "agotado"

class Nodo:
    def __init__(self, nombre, posicion, peso=None, altura=None, estante=None,
                 estacion=False, recharge_rate=0):
        self.nombre = nombre
        self.posicion = posicion
        self.peso = peso
        self.altura = altura
        self.estante = estante
        self.estacion = estacion
        self.recharge_rate = recharge_rate
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
        return Paquete(producto=producto, peso=random.uniform(1, 10))
    

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

        self.ocupacion = 0

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
    def __init__(self, id, position, consumo=1):
        self.id = id
        self.position = position
        self.target = None
        self.distance = 0
        self.capacidad_carga = 0
        self.autonomia = 100
        self.actividad = Actividad.ESPERA.value
        self.nivel_bateria = NivelBateria.OPERATIVO.value
        self.actividad_prevista = None
        self.target_previsto = None
        # self.disponible = True
        self.continuous_position = None
        self.path = []
        self.current_edge_index = 0
        self.progress_along_edge = 0.0
        self.paquete_actual = None
        self.edge_times = []
        self.recharge_pending = False
        self.consumo = consumo
        self.stuck_counter = 0

    
    def consumir_energia(self, dist, peso=0):
        """Consume energía en función de ``self.consumo``.

        Los parámetros ``dist`` y ``peso`` se mantienen por compatibilidad
        pero el consumo final depende únicamente del valor configurable
        ``self.consumo``.
        """
        self.autonomia = max(self.autonomia - self.consumo, 0)
        if self.autonomia <= 0:
            self.autonomia = 0
        self._actualizar_nivel_bateria()

    def recargar(self, cantidad):
        """Aumenta la autonomía del robot hasta un máximo de 100."""
        if self.actividad != Actividad.RECARGA.value:
            return
        self.autonomia = min(self.autonomia + cantidad, 100)
        self._actualizar_nivel_bateria()
        if self.autonomia >= 100 and self.nivel_bateria == NivelBateria.OPERATIVO.value:
            self.reanudar_tarea()

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

    def _actualizar_nivel_bateria(self):
        if self.autonomia <= 0:
            self.nivel_bateria = NivelBateria.AGOTADO.value
        elif self.autonomia <= 25:
            self.nivel_bateria = NivelBateria.CRITICO.value
        elif self.autonomia < 40:
            self.nivel_bateria = NivelBateria.LIMITADO.value
        else:
            self.nivel_bateria = NivelBateria.OPERATIVO.value

    def set_actividad(self, nueva):
        if nueva not in [a.value for a in Actividad]:
            raise ValueError(f"Actividad '{nueva}' no válida")
        self.actividad = nueva

    def set_nivel_bateria(self, nuevo):
        if nuevo not in [n.value for n in NivelBateria]:
            raise ValueError(f"Nivel '{nuevo}' no válido")
        self.nivel_bateria = nuevo

    def pausar_tarea(self):
        self.actividad_prevista = self.actividad
        self.target_previsto = self.target
        self.set_actividad(Actividad.DIRIGIENDOSE_A_RS.value)
        self.target = None
        self.path = []
        self.edge_times = []
        self.current_edge_index = 0
        self.progress_along_edge = 0.0

    def reanudar_tarea(self):
        if self.actividad_prevista is not None:
            self.actividad = self.actividad_prevista
            self.target = self.target_previsto
            self.actividad_prevista = None
            self.target_previsto = None


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

    def __init__(self, producto=None, posicion=None, peso = None):
        self.producto = producto if producto else "Otro"
        self.posicion = posicion
        self.peso = peso if peso is not None else random.uniform(1, 10)


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
        return f"Paquete que contiene: {self.producto} (peso: {self.peso:.2f})"

    @classmethod
    def mostrar_productos_disponibles(cls):
        """Muestra la lista de productos disponibles."""
        print("Productos disponibles:")
        for producto in cls.productos_disponibles:
            print(f"- {producto}")
            




