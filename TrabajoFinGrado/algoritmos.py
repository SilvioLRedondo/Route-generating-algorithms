import heapq

def a_star_search(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for neighbor in graph.neighbors(current):
            arista = graph[current][neighbor]['objeto_arista']
            new_cost = cost_so_far[current] + arista.get_peso() + arista.longitud()
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))
                came_from[neighbor] = current
    
    if goal not in came_from:
        # Si no se encontró ruta posible devolvemos una lista vacía
        return []

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    return path[::-1]