from Clases import Prioridad


class EdgeReservations:
    """Manage reservations of edges over discrete time steps."""

    def __init__(self):
        # mapping (node_a, node_b) -> {time_step: [robot_ids]}
        self.reservations = {}

    def _edge_key(self, edge):
        u, v = edge
        return tuple(sorted((u, v)))

    def is_available(self, edge, time_step, capacity=2):
        """Return True if the edge is free at the given time step."""
        key = self._edge_key(edge)
        times = self.reservations.get(key, {})
        reserved = times.get(time_step, [])
        return len(reserved) < capacity

    def reserve_path(self, robot_id, path, start_time, graph=None, capacity=2):
        """Reserve consecutive edges of ``path`` starting at ``start_time``.

        If ``graph`` is provided the capacity of each edge is taken from the
        graph's ``objeto_arista.capacidad`` attribute. Otherwise ``capacity`` is
        used as a uniform limit.

        Returns ``True`` if all reservations succeed. If any edge/time slot is
        already at capacity the method leaves existing reservations untouched and
        returns ``False``.
        """
        time = start_time
        pending = []
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            key = self._edge_key(edge)
            self.reservations.setdefault(key, {})
            edge_capacity = capacity
            if graph is not None and graph.has_edge(*edge):
                edge_capacity = graph[edge[0]][edge[1]]["objeto_arista"].capacidad
            if len(self.reservations[key].get(time, [])) >= edge_capacity:
                return False
            pending.append((key, time))
            time += 1

        for key, t in pending:
            self.reservations[key].setdefault(t, []).append(robot_id)
        return True

    def release_before(self, time_step):
        """Remove reservations for times older than ``time_step``."""
        for key in list(self.reservations.keys()):
            times = self.reservations[key]
            for t in list(times.keys()):
                if t < time_step:
                    del times[t]
            if not times:
                del self.reservations[key]

    def release_robot(self, robot_id):
        """Remove all reservations made by ``robot_id``."""
        for key in list(self.reservations.keys()):
            times = self.reservations[key]
            for t in list(times.keys()):
                if robot_id in times[t]:
                    times[t].remove(robot_id)
                if not times[t]:
                    del times[t]
            if not times:
                del self.reservations[key]


class HileraReservations:
    """Manage time reservations for entire columns (hileras)."""

    def __init__(self, default_capacity=1, capacities=None):
        self.default_capacity = default_capacity
        self.capacities = capacities or {}
        # mapping column_id -> {time_step: [(robot_id, prioridad)]}
        self.reservations = {}

    def _capacity(self, column_id):
        return self.capacities.get(column_id, self.default_capacity)

    def is_available(self, column_id, time_step, prioridad):
        times = self.reservations.get(column_id, {})
        reserved = times.get(time_step, [])
        if len(reserved) < self._capacity(column_id):
            return True
        if prioridad == Prioridad.URGENTE and reserved:
            lowest = min(reserved, key=lambda x: x[1])
            return lowest[1] < Prioridad.URGENTE
        return False

    def reserve(self, column_id, time_step, robot_id, prioridad):
        times = self.reservations.setdefault(column_id, {})
        slot = times.setdefault(time_step, [])
        if len(slot) < self._capacity(column_id):
            slot.append((robot_id, prioridad))
            return None
        if prioridad == Prioridad.URGENTE and slot:
            lowest = min(slot, key=lambda x: x[1])
            if lowest[1] < Prioridad.URGENTE:
                slot.remove(lowest)
                slot.append((robot_id, prioridad))
                return lowest[0]
        return False

    def release_before(self, time_step):
        for col in list(self.reservations.keys()):
            times = self.reservations[col]
            for t in list(times.keys()):
                if t < time_step:
                    del times[t]
            if not times:
                del self.reservations[col]
