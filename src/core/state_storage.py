
class StateStorage:
    """Tracks explored states and solution paths."""
    def __init__(self):
        self.states = set()  # Use a set for O(1) lookup
        self.parent = {}     # Store parent states for solution reconstruction
        self.move = {}       # Store the move that led to each state
    
    def add_state(self, state, parent_state=None, move=None):
        """Add a state to storage with its parent state and the move that led to it"""
        state_hash = hash(state)
        if state_hash not in self.states:
            self.states.add(state_hash)
            if parent_state is not None:
                self.parent[state_hash] = parent_state
                self.move[state_hash] = move
            return True
        return False
    
    def has_state(self, state):
        """Check if a state has been seen before"""
        return hash(state) in self.states
    
    def get_path(self, final_state):
        """Reconstruct the path from initial to final state"""
        path = []
        current_hash = hash(final_state)
        
        while current_hash in self.parent:
            path.append(self.move[current_hash])
            current_hash = hash(self.parent[current_hash])
        
        return list(reversed(path))  