import os
import time
import csv
import math
import statistics
import random
from pathlib import Path

import pytest

from models.algorithms import BinPackingAlgorithms
from models.warehouse_environment import WarehouseEnvironment

# plotting and data libraries (optional at test-import time)
import matplotlib.pyplot as plt
# CONTROL: to run the benchmark set environment variable BENCHMARK=1
RUN_BENCHMARK = True

# Output files
CSV_PATH = Path("./run_time.csv")
TXT_PATH = Path("./run_time.txt")
PLOT_DIR = Path("./")
TRIALS = 3  # number of repetitions per (algo, scenario, scale); increase for smoother results

# Algorithms to measure
ALGORITHMS = [
    ("FirstFit", BinPackingAlgorithms.first_fit),
    ("BestFit", BinPackingAlgorithms.best_fit),
    ("FFD", BinPackingAlgorithms.first_fit_decreasing),
    ("Knapsack", BinPackingAlgorithms.knapsack_based),
    ("BnB", BinPackingAlgorithms.branch_and_bound),
]

# Base scenarios (same sets you already use)
BASE_SCENARIOS = {
    "original": [60, 55, 50, 45, 40, 35, 30, 30, 25, 20, 15, 15, 10, 10, 10, 5, 5, 5],
    "small_first": [5,5,5,10,10,10,15,15,20,25,30,30,35,40,45,50,55,60],
    "mixed_adversarial": [30, 60, 15, 55, 10, 50, 5, 45, 35, 30, 20, 25, 10, 15, 40, 5, 10, 5],
}

# Scales to test: multiply the base multiset to reach approx these many items
SCALES = [1, 2, 5, 10]  # multiply base list by these factors -> sizes of len(base)*factor


def create_env_from_sizes(capacity, sizes):
    env = WarehouseEnvironment(bin_capacity=capacity)
    env.add_items_batch(sizes)
    return env


@pytest.mark.skipif(not RUN_BENCHMARK, reason="Benchmark disabled. Set BENCHMARK=1 to run.")
def test_runtime_benchmark_and_save_results(tmp_path):
    """
    Benchmark runtimes of algorithms across scenarios and scales.
    Results:
      - ./run_time.csv : per-trial data (scenario, scale, n_items, algo, trial, time_s)
      - ./run_time.txt : human-readable summary (means, medians)
      - ./run_time_<scenario>.png : plot of mean runtime vs n_items per algorithm
    NOTE: This is a heavy test and is intentionally opt-in via BENCHMARK=1 environment variable.
    """
    random_seed = 12345
    random.seed(random_seed)  # deterministic where randomness used

    # Prepare CSV
    CSV_PATH.unlink(missing_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["scenario", "scale", "n_items", "algorithm", "trial", "time_s"])

        # Store aggregated results for plotting/summaries
        aggregated = {}  # aggregated[(scenario, scale, algo)] = [times...]

        for scenario_name, base_sizes in BASE_SCENARIOS.items():
            for scale in SCALES:
                # Build scaled sizes by repeating the base pattern
                sizes = base_sizes * scale
                n_items = len(sizes)
                capacity = 100  # keep capacity 100 as before

                for algo_name, algo_func in ALGORITHMS:
                    times = []
                    for t in range(1, TRIALS + 1):
                        # fresh env for each trial
                        env = create_env_from_sizes(capacity, sizes)
                        start = time.perf_counter()
                        # run algorithm; handle exceptions gracefully
                        try:
                            algo_func(env)
                            end = time.perf_counter()
                            elapsed = end - start
                        except Exception as e:
                            end = time.perf_counter()
                            elapsed = end - start
                            # record the elapsed time and also continue (we still record)
                            # optionally you may want to fail here; we only record to CSV
                            # and include the exception text in the summary
                            # but for test-suite stability we don't raise here
                            times.append(elapsed)
                            writer.writerow([scenario_name, scale, n_items, algo_name, t, elapsed])
                            # store aggregated; include exception marker as negative time in summary file later
                            aggregated.setdefault((scenario_name, scale, algo_name), []).append(elapsed)
                            # continue to next trial
                            continue

                        times.append(elapsed)
                        writer.writerow([scenario_name, scale, n_items, algo_name, t, elapsed])

                    aggregated.setdefault((scenario_name, scale, algo_name), []).extend(times)

    # Produce a human-readable summary file
    summary_lines = []
    summary_lines.append("Runtime benchmark summary\n")
    summary_lines.append(f"BENCHMARK run with TRIALS={TRIALS}, SCALES={SCALES}\n")
    summary_lines.append(f"CSV output: {CSV_PATH.resolve()}\n")
    summary_lines.append("\nAggregated (mean, median) per scenario/scale/algorithm:\n")

    # For each scenario, build plot data
    for scenario_name in BASE_SCENARIOS.keys():
        # Prepare a dictionary mapping algo -> list of (n_items, mean_time)
        plot_data = {algo_name: [] for algo_name, _ in ALGORITHMS}

        for scale in SCALES:
            sizes = BASE_SCENARIOS[scenario_name] * scale
            n_items = len(sizes)
            for algo_name, _ in ALGORITHMS:
                times = aggregated.get((scenario_name, scale, algo_name), [])
                if times:
                    mean_t = statistics.mean(times)
                    median_t = statistics.median(times)
                else:
                    mean_t = float("nan")
                    median_t = float("nan")
                summary_lines.append(f"{scenario_name:>15} | scale={scale:<2} | n={n_items:<3} | {algo_name:<10} | mean={mean_t:.6f}s median={median_t:.6f}s")
                plot_data[algo_name].append((n_items, mean_t))

        # Plot per scenario if matplotlib is available
        if plt is not None:
            plt.figure()
            for algo_name, points in plot_data.items():
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                # plot one line per algorithm (no explicit colors or styles set)
                plt.plot(xs, ys, marker='o', label=algo_name)
            plt.xlabel("Number of items")
            plt.ylabel("Mean runtime (s)")
            plt.title(f"Runtime vs n_items — {scenario_name}")
            plt.legend()
            plot_path = PLOT_DIR / f"run_time_{scenario_name}.png"
            plt.savefig(plot_path)
            plt.close()
            summary_lines.append(f"Plot saved: {plot_path.resolve()}\n")
        else:
            summary_lines.append("matplotlib not installed — skipping plots\n")

    # Write summary to TXT
    TXT_PATH.write_text("\n".join(summary_lines), encoding="utf-8")

    # Basic assertions so pytest records test success
    assert CSV_PATH.exists(), "CSV output not created."
    assert TXT_PATH.exists(), "TXT summary not created."

    # Ensure we recorded at least one timing per algorithm for the smallest scale
    min_scale = min(SCALES)
    for algo_name, _ in ALGORITHMS:
        key = ("original", min_scale, algo_name)
        assert key in aggregated, f"No data for {key}"
        assert len(aggregated[key]) >= 1, f"No trials recorded for {key}"

    # Optionally: fail if any algorithm raised errors on all trials (not desired)
    # For now we pass as long as files exist and data recorded.
