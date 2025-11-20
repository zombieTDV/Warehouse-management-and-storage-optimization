import itertools
import pytest

from models.algorithms import BinPackingAlgorithms
from models.warehouse_environment import WarehouseEnvironment, Item


def flatten_bin_items(bins):
    """Return a list of Items contained in bins (preserving object identity)."""
    items = []
    for b in bins:
        items.extend(getattr(b, 'items', []))
    return items


def total_sizes(items):
    return sum(getattr(it, 'size', it) for it in items)


def create_env_from_sizes(capacity, sizes):
    env = WarehouseEnvironment(bin_capacity=capacity)
    env.add_items_batch(sizes)
    return env


@pytest.mark.parametrize("sizes,capacity", [
    # The dataset the user used (should be reasonably packable)
    ([60, 55, 50, 45, 40, 35, 30, 30, 25, 20, 15, 15, 10, 10, 10, 5, 5, 5], 100),

    # Small-first ordering (often hurts plain First Fit)
    ([5,5,5,10,10,10,15,15,20,25,30,30,35,40,45,50,55,60], 100),

    # Mixed/adversarial-ish ordering
    ([30, 60, 15, 55, 10, 50, 5, 45, 35, 30, 20, 25, 10, 15, 40, 5, 10, 5], 100),
])
def test_all_algorithms_produce_valid_packings(sizes, capacity):
    """
    For each algorithm:
      - No bin exceeds capacity.
      - All items are placed exactly once (by total size).
      - The returned number of bins equals len(env.bins).
    """
    algos = [
        ("FirstFit", BinPackingAlgorithms.first_fit),
        ("BestFit", BinPackingAlgorithms.best_fit),
        ("FFD", BinPackingAlgorithms.first_fit_decreasing),
        ("Knapsack", BinPackingAlgorithms.knapsack_based),
        ("BnB", BinPackingAlgorithms.branch_and_bound),
    ]

    # total size of items (ground truth)
    total_size = sum(sizes)

    for name, algo in algos:
        # create a fresh environment for each algorithm to avoid side-effects
        env = create_env_from_sizes(capacity, sizes)
        bins, num_bins = algo(env)

        # number of bins equals return value
        assert num_bins == len(bins), f"{name}: returned num_bins doesn't match len(bins)"

        # check no bin exceeds capacity, and compute used space
        used = 0
        seen_items = []
        for b in bins:
            # b.capacity may be attribute or env.bin_capacity
            cap = getattr(b, 'capacity', capacity)
            # compute bin used size by summing item.size
            b_items = getattr(b, 'items', [])
            b_used = sum(it.size for it in b_items)
            assert b_used <= cap, f"{name}: bin over capacity ({b_used} > {cap})"
            used += b_used
            seen_items.extend(b_items)

        # All items placed: sum of assigned sizes == total_size
        assert used == total_size, f"{name}: total used {used} != total items size {total_size}"

        # Count items by size to ensure multiplicities match (in case same-size items are separate objects)
        # Build multiset of sizes from original sizes and from placed items
        original_multiset = {}
        for s in sizes:
            original_multiset[s] = original_multiset.get(s, 0) + 1
        placed_multiset = {}
        for it in seen_items:
            placed_multiset[it.size] = placed_multiset.get(it.size, 0) + 1
        assert original_multiset == placed_multiset, f"{name}: placed items multiset != original (placed {placed_multiset}, original {original_multiset})"


def brute_force_best_subset_sum(sizes, capacity):
    """Return maximum achievable sum <= capacity by checking all subsets (for small n)."""
    best = 0
    best_subset = ()
    n = len(sizes)
    for mask in range(1 << n):
        s = 0
        subset = []
        for i in range(n):
            if (mask >> i) & 1:
                s += sizes[i]
                subset.append(i)
        if s <= capacity and s > best:
            best = s
            best_subset = tuple(subset)
    return best, best_subset


def test_solve_knapsack_returns_optimal_subset_for_small_instance():
    """
    Validate _solve_knapsack by comparing its chosen subset sum to a brute-force optimum
    on a small instance (n <= 10).
    """
    # small instance (n <= 10)
    sizes = [20, 35, 10, 5, 30]  # sum=100, capacity 60
    capacity = 60

    env = create_env_from_sizes(capacity, sizes)
    # items objects as in env.items
    items = env.items[:]  # list of Item objects

    chosen = BinPackingAlgorithms._solve_knapsack(items, capacity)
    chosen_sum = sum(it.size for it in chosen)

    # compute brute-force best sum
    best_sum, best_subset = brute_force_best_subset_sum(sizes, capacity)

    assert chosen_sum == best_sum, f"Knapsack returned sum {chosen_sum}, brute-force best is {best_sum}"


def test_branch_and_bound_is_at_least_as_good_as_heuristics():
    """
    For each dataset run, branch_and_bound should return a packing
    whose number of bins is <= the number of bins produced by the greedy heuristics.
    (Branch & Bound is intended to be optimal.)
    """
    sizes = [60, 55, 50, 45, 40, 35, 30, 30, 25, 20, 15, 15, 10, 10, 10, 5, 5, 5]
    capacity = 100

    # run heuristics and b&b on fresh envs
    env_ff = create_env_from_sizes(capacity, sizes)
    ff_bins, ff_n = BinPackingAlgorithms.first_fit(env_ff)

    env_bf = create_env_from_sizes(capacity, sizes)
    bf_bins, bf_n = BinPackingAlgorithms.best_fit(env_bf)

    env_ffd = create_env_from_sizes(capacity, sizes)
    ffd_bins, ffd_n = BinPackingAlgorithms.first_fit_decreasing(env_ffd)

    env_dp = create_env_from_sizes(capacity, sizes)
    dp_bins, dp_n = BinPackingAlgorithms.knapsack_based(env_dp)

    env_bb = create_env_from_sizes(capacity, sizes)
    bb_bins, bb_n = BinPackingAlgorithms.branch_and_bound(env_bb)

    # branch and bound should be <= min of others (optimal or equal)
    min_heuristic = min(ff_n, bf_n, ffd_n, dp_n)
    assert bb_n <= min_heuristic, (
        f"Branch&Bound returned {bb_n} bins but heuristics found as low as {min_heuristic}. "
        "Branch&Bound should be optimal or equal."
    )


@pytest.mark.parametrize("sizes,capacity", [
    ([5,5,5,5,5,5,5,5], 10),   # many small items; check correctness
    ([9,9,2,2,2,2,2], 10),     # requires mixing to reach capacity
])
def test_knapsack_based_packs_each_bin_most_fully(sizes, capacity):
    """
    The knapsack-based algorithm should fill each created bin with a maximal-sum subset
    (locally optimal for that bin). We check for the first bin that its sum equals
    the brute-force best sum for that capacity given the initial items.
    """
    env = create_env_from_sizes(capacity, sizes)
    # call knapsack_based
    bins, num_bins = BinPackingAlgorithms.knapsack_based(env)

    assert len(bins) >= 1
    first_bin_items = getattr(bins[0], 'items', [])
    first_sum = sum(it.size for it in first_bin_items)

    # compute brute-force optimal for the original sizes
    best_sum, _ = brute_force_best_subset_sum(sizes, capacity)
    assert first_sum == best_sum, "Knapsack-based should pick a maximal subset for first bin"
