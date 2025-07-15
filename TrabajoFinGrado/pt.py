import funTFG
import networkx as nx
import matplotlib.pyplot as plt

n, m, k, d = 12, 12, 144, 5


rs = 1

G = funTFG.GraphGen(n,m,k,d)

print(len(G))

# Obtener la posicion de los nodos para que el grafo no cambie entre dibujos
pos = {node: node.posicion for node in G.nodes()}

# Dibujar el grafo
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=400)

# Dibujar los pesos de las aristas
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Mostrar el grafo
plt.title("Grafo con pesos en las aristas")
plt.show()
