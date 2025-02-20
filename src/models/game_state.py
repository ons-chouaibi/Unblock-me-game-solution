from src.models.vehicle import Vehicle

class GameState:
    """Represents a unique game state for tracking visited states."""
    def __init__(self, vehicles, grid_size):
        self.vehicles = sorted(vehicles, key=lambda v: v.label)
        self.grid_size = grid_size
        self._hash = None
    
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        if len(self.vehicles) != len(other.vehicles):
            return False
        return all(v1.label == v2.label and 
                  v1.x == v2.x and 
                  v1.y == v2.y and 
                  v1.orientation == v2.orientation and 
                  v1.length == v2.length 
                  for v1, v2 in zip(self.vehicles, other.vehicles))
    
    def __hash__(self):
        if self._hash is None:
            # Create a tuple of immutable attributes for each vehicle
            vehicle_tuples = tuple(
                (v.label, v.orientation, v.length, v.x, v.y)
                for v in self.vehicles
            )
            self._hash = hash(vehicle_tuples)
        return self._hash

class PrioritizedState:
    def __init__(self, game, state, moves, heuristic_value):
        self.game = game
        self.state = state
        self.moves = moves
        self.heuristic_value = heuristic_value
        self.priority = moves + heuristic_value  # f(n) = g(n) + h(n)

    def __lt__(self, other):
        return self.priority < other.priority