import heapq


def a_star_search(graph, start, goal, obstacles=None):
    if obstacles is None:
        obstacles = set()
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for neighbor in graph.neighbors(current):
            if neighbor in obstacles:
                continue
            arista = graph[current][neighbor]['objeto_arista']
            new_cost = cost_so_far[current] + arista.get_peso() + arista.longitud()
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        return []

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    return path[::-1]


def a_star_with_reservations(graph, start, goal, start_time, reservations, obstacles=None):
    if obstacles is None:
        obstacles = set()
    """A* search that avoids edges reserved at specific times."""
    start_state = (start, start_time)
    frontier = []
    heapq.heappush(frontier, (0, start_state))
    came_from = {start_state: None}
    cost_so_far = {start_state: 0}

    while frontier:
        _, (current_node, current_time) = heapq.heappop(frontier)
        if current_node == goal:
            goal_state = (current_node, current_time)
            break
        for neighbor in graph.neighbors(current_node):
            if neighbor in obstacles:
                continue
            arista = graph[current_node][neighbor]['objeto_arista']
            next_time = current_time + 1
            if not reservations.is_available((current_node, neighbor), next_time, arista.capacidad):
                continue
            next_state = (neighbor, next_time)
            new_cost = cost_so_far[(current_node, current_time)] + 1
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                heapq.heappush(frontier, (new_cost, next_state))
                came_from[next_state] = (current_node, current_time)
    else:
        return [], []

    # reconstruct path and times
    path = []
    times = []
    state = goal_state
    while state:
        node, time = state
        path.append(node)
        prev = came_from[state]
        if prev:
            times.append(prev[1] + 1)
        state = prev
    path.reverse()
    times.reverse()
    return path, times
