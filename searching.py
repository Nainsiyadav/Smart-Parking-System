import time


def linear_search(vehicle_list, target):
    for vehicle in vehicle_list:
        if vehicle == target:
            return True
    return False


def binary_search(vehicle_list, target):
    low = 0
    high = len(vehicle_list) - 1

    while low <= high:
        middle = (low + high) // 2

        if vehicle_list[middle] == target:
            return True
        elif vehicle_list[middle] < target:
            low = middle + 1
        else:
            high = middle - 1

    return False


def bubble_sort(vehicle_list):
    data = vehicle_list.copy()
    n = len(data)

    for i in range(n - 1):
        swapped = False

        for j in range(n - 1 - i):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True

        if not swapped:
            break

    return data


def test_search():
    sizes = [10, 100, 1000, 10000, 100000]

    print("\nSEARCHING ALGORITHM TEST")
    print("\nSize\tLinear Search\tBinary Search")

    results = []

    for size in sizes:
        vehicles = []
        for i in range(size):
            vehicles.append("MH01AB" + str(i).zfill(5))

        target = vehicles[-1]

        start = time.perf_counter()
        linear_search(vehicles, target)
        linear_time = time.perf_counter() - start

        # Bubble Sort is demonstrated separately below. For the large
        # performance experiment, the data is already sorted, so we do
        # not mix sorting time into binary-search timing.
        sorted_vehicles = vehicles.copy()

        start = time.perf_counter()
        binary_search(sorted_vehicles, target)
        binary_time = time.perf_counter() - start

        results.append((size, linear_time, binary_time))

        print(size, "\t", round(linear_time, 8), "\t", round(binary_time, 8))

    print("\nSEARCHING ALGORITHM COMPARISON")
    for size, linear_time, binary_time in results:
        faster = "Linear Search" if linear_time < binary_time else "Binary Search"
        print(size, "records ->", faster, "is faster")

    print("\nCOMPLEXITY COMPARISON")
    print("Linear Search -> O(n)")
    print("Binary Search -> O(log n)")
    print("Bubble Sort -> O(n²)")

    print("\nCONCLUSION")
    print("Linear Search is simple but becomes slower as the number of vehicles increases.")
    print("Binary Search is efficient for large sorted datasets.")


def test_bubble_sort():
    sample = ["MH01AB1000", "MH01AB0002", "MH01AB0050", "MH01AB0001"]
    sorted_sample = bubble_sort(sample)

    print("\nBUBBLE SORT TEST")
    print("Before:", sample)
    print("After:", sorted_sample)
    print("Sorted correctly:", sorted_sample == sorted(sample))


if __name__ == "__main__":
    test_search()
    test_bubble_sort()
