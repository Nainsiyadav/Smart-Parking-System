import time
from pathlib import Path

import matplotlib.pyplot as plt

from searching import binary_search, linear_search


def measure_search_performance():
    sizes = [10, 100, 1000, 10000, 100000]
    linear_times = []
    binary_times = []

    for size in sizes:
        vehicles = ["MH01AB" + str(i).zfill(5) for i in range(size)]
        target = vehicles[-1]

        # Average several runs to reduce timing noise.
        repeats = 10

        start = time.perf_counter()
        for _ in range(repeats):
            linear_search(vehicles, target)
        linear_time = (time.perf_counter() - start) / repeats

        sorted_vehicles = vehicles.copy()
        start = time.perf_counter()
        for _ in range(repeats):
            binary_search(sorted_vehicles, target)
        binary_time = (time.perf_counter() - start) / repeats

        linear_times.append(linear_time)
        binary_times.append(binary_time)

        print(
            f"{size:>6} records | "
            f"Linear: {linear_time:.8f}s | "
            f"Binary: {binary_time:.8f}s"
        )

    return sizes, linear_times, binary_times


def generate_graph():
    print("\nSEARCH PERFORMANCE ANALYSIS")
    sizes, linear_times, binary_times = measure_search_performance()

    graph_file = Path(__file__).resolve().with_name("search_performance.png")

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, linear_times, marker="o", label="Linear Search")
    plt.plot(sizes, binary_times, marker="o", label="Binary Search")
    plt.xlabel("Number of Vehicles")
    plt.ylabel("Average Search Time (seconds)")
    plt.title("Linear Search vs Binary Search")
    plt.xscale("log")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(graph_file, dpi=150)
    plt.close()

    print("\nGraph saved as:", graph_file.name)
    return graph_file


if __name__ == "__main__":
    generate_graph()
