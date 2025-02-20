
class Vehicle:
    """Represents a vehicle in the puzzle with attributes for position and orientation."""
    def __init__(self, label, orientation, length, x, y):
        self.label = label
        self.orientation = orientation  # 'h' for horizontal, 'v' for vertical
        self.length = length
        self.x = x # Column index (starting position)
        self.y = y  # Row index (starting position)

    def __repr__(self):
        return f"Vehicle({self.label}, {self.orientation}, {self.length}, {self.x}, {self.y})"