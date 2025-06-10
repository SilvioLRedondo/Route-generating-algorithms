class EdgeReservations:
    """Manage reservations of edges over discrete time steps."""

    def __init__(self):
        # mapping (node_a, node_b) -> {time_step: [robot_ids]}
        self.reservations = {}

    def _edge_key(self, edge):
        u, v = edge
        return (u, v)

    def is_available(self, edge, time_step, capacity=2):
        """Return True if the edge is free at the given time step."""
        key = self._edge_key(edge)
        times = self.reservations.get(key, {})
        reserved = times.get(time_step, [])
        return len(reserved) < capacity

    def reserve_path(self, robot_id, path, start_time, capacity=2):
        """Reserve consecutive edges of ``path`` starting at ``start_time``."""
        time = start_time
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            key = self._edge_key(edge)
            self.reservations.setdefault(key, {}).setdefault(time, []).append(robot_id)
            time += 1

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
