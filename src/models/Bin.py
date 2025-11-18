# binpacking_storage.py
from typing import List

class Bin:
    """Simple Bin with fixed capacity that holds item sizes (floats or ints)."""

    def __init__(self, capacity: float):
        if capacity <= 0:
            raise ValueError("Bin capacity must be > 0")
        self.capacity: float = float(capacity)
        self.items: List[float] = []

    def free_space(self) -> float:
        """Return remaining free space in the bin."""
        return self.capacity - sum(self.items)

    def load(self) -> float:
        """Return used space in the bin."""
        return sum(self.items)

    def can_fit(self, item_size: float) -> bool:
        """Return True if item_size can be placed into this bin."""
        if item_size < 0:
            raise ValueError("item_size must be non-negative")
        return item_size <= self.free_space()

    def add(self, item_size: float) -> None:
        """Place an item into the bin. Raises ValueError if it doesn't fit."""
        if not self.can_fit(item_size):
            raise ValueError(f"Item {item_size} does not fit in bin (free {self.free_space()})")
        self.items.append(float(item_size))

    def remove_last(self) -> float:
        """Remove and return the last added item. Raises IndexError if empty."""
        if not self.items:
            raise IndexError("remove_last: no items in bin")
        return self.items.pop()

    def __repr__(self) -> str:
        return f"Bin(cap={self.capacity}, load={self.load():.3f}, items={self.items})"

