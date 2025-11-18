from .Bin import Bin

from typing import List, Optional, Tuple
import copy

class Storage:
    """
    Storage: container for many Bins and the current assignment state for a list of items.
    - items: list of item sizes (fixed order)
    - bins: list[Bin]
    - assignment: list[int] where assignment[i] = index of bin containing item i, or -1 if unplaced
    """

    def __init__(self, items: List[float], bin_capacity: float, allow_new_bin_on_move: bool = True):
        """
        items: list of non-negative sizes
        bin_capacity: capacity for each bin
        allow_new_bin_on_move: if True, move(item, bin_index=None) will create a new bin automatically
        """
        if bin_capacity <= 0:
            raise ValueError("bin_capacity must be > 0")
        if any(s < 0 for s in items):
            raise ValueError("item sizes must be non-negative")

        self.items: List[float] = [float(s) for s in items]
        self.n = len(self.items)
        self.bin_capacity = float(bin_capacity)
        self.bins: List[Bin] = []
        self.assignment: List[int] = [-1] * self.n  # -1 means unplaced
        # stack to allow undo operations: list of (item_index, bin_index)
        self._history: List[Tuple[int, int]] = []
        self.allow_new_bin_on_move = allow_new_bin_on_move

    # ----------------- basic runtime functions -----------------
    def reset(self):
        """Clear all bins and assignments (start from scratch)."""
        self.bins = []
        self.assignment = [-1] * self.n
        self._history = []

    def clone(self) -> "Storage":
        """Return a deep copy of the storage (useful for search tree branching)."""
        return copy.deepcopy(self)

    def current_assignments(self) -> List[int]:
        """Return a copy of current assignment list."""
        return list(self.assignment)

    def bins_state(self) -> List[Bin]:
        """Return list of bins (objects). Be careful mutating them — use clone() to explore."""
        return self.bins

    # ----------------- move / undo -----------------
    def move(self, item_index: int, bin_index: Optional[int] = None) -> int:
        """
        Place item `item_index` into bin `bin_index`.
        - If bin_index is None and `allow_new_bin_on_move` is True, create a new bin and put the item there.
        - Returns the bin index where the item was placed.
        - Raises:
            IndexError if item_index invalid
            ValueError if item already placed or item doesn't fit and no new bin allowed
        """
        if not (0 <= item_index < self.n):
            raise IndexError("move: item_index out of range")
        if self.assignment[item_index] != -1:
            raise ValueError(f"move: item {item_index} already placed in bin {self.assignment[item_index]}")

        item_size = self.items[item_index]

        # choose existing bin
        if bin_index is not None:
            if not (0 <= bin_index < len(self.bins)):
                raise IndexError("move: bin_index out of range")
            if not self.bins[bin_index].can_fit(item_size):
                raise ValueError(f"move: item {item_index} size {item_size} doesn't fit into bin {bin_index}")
            self.bins[bin_index].add(item_size)
            self.assignment[item_index] = bin_index
            self._history.append((item_index, bin_index))
            return bin_index

        # bin_index is None: create new bin if allowed
        if self.allow_new_bin_on_move:
            new_bin = Bin(self.bin_capacity)
            if not new_bin.can_fit(item_size):
                raise ValueError(f"move: item {item_index} size {item_size} > bin capacity {self.bin_capacity}")
            new_bin.add(item_size)
            self.bins.append(new_bin)
            new_index = len(self.bins) - 1
            self.assignment[item_index] = new_index
            self._history.append((item_index, new_index))
            return new_index

        raise ValueError("move: bin_index is None and new bins are disabled")

    def undo_move(self) -> Tuple[int, int]:
        """
        Undo the last move. Returns (item_index, bin_index) that was undone.
        Raises IndexError if no moves to undo.
        If the bin becomes empty after undo, the bin remains (so bin indexes stay stable).
        """
        if not self._history:
            raise IndexError("undo_move: no moves to undo")
        item_index, bin_index = self._history.pop()
        # remove last item from that bin and mark unplaced
        removed = self.bins[bin_index].remove_last()
        assert abs(removed - self.items[item_index]) < 1e-9, "undo_move: removed item size mismatch"
        self.assignment[item_index] = -1
        return item_index, bin_index

    # ----------------- query helpers -----------------
    def can_move(self, item_index: int, bin_index: int) -> bool:
        """Check if item can be placed in a specific bin (without changing state)."""
        if not (0 <= item_index < self.n):
            raise IndexError("can_move: item_index out of range")
        if not (0 <= bin_index < len(self.bins)):
            raise IndexError("can_move: bin_index out of range")
        if self.assignment[item_index] != -1:
            return False
        return self.bins[bin_index].can_fit(self.items[item_index])

    def possible_bins_for_item(self, item_index: int) -> List[int]:
        """Return indices of all bins where this item can be placed (existing bins)."""
        if not (0 <= item_index < self.n):
            raise IndexError("possible_bins_for_item: item_index out of range")
        result = []
        for i, b in enumerate(self.bins):
            if b.can_fit(self.items[item_index]):
                result.append(i)
        return result

    def possible_moves_for_item(self, item_index: int) -> List[Optional[int]]:
        """
        Return a list of possible moves for an item:
          [0,2,5,None] meaning can place in bin 0, 2, 5 or create a new bin (None).
        (None present only if allow_new_bin_on_move is True and item fits in an empty bin).
        """
        moves = self.possible_bins_for_item(item_index)
        if self.allow_new_bin_on_move:
            # check if item fits into an empty fresh bin
            if self.items[item_index] <= self.bin_capacity:
                moves.append(None)
        return moves

    def bins_loads(self) -> List[float]:
        """Return current loads of each bin (used space)."""
        return [b.load() for b in self.bins]

    def total_bins_used(self) -> int:
        return len(self.bins)

    def unplaced_items(self) -> List[int]:
        """Return indices of items not yet placed."""
        return [i for i, a in enumerate(self.assignment) if a == -1]

    def __repr__(self) -> str:
        return f"Storage(bins={self.bins}, assignment={self.assignment})"
