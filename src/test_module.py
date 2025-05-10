def binary_search(arr, target):
    """
    Performs binary search on a sorted array to find the target element.

    Args:
        arr: A sorted list or array of elements.
        target: The value to search for in the array.

    Returns:
        The index of the target element if found, otherwise -1.
    """
    low = 0  # Initialize the lower bound of the search space
    high = len(arr) - 1  # Initialize the upper bound of the search space

    while low <= high:  # Continue searching as long as the search space is valid
        mid = (low + high) // 2  # Calculate the middle index (integer division)

        if arr[mid] == target:
            return mid  # Target found at the middle index
        elif arr[mid] < target:
            low = mid + 1  # Target is in the right half, update the lower bound
        else:  # arr[mid] > target
            high = mid - 1  # Target is in the left half, update the upper bound

    return -1  # Target not found in the array

def insertion_sort(arr):
    """
    Sorts a list in-place using the insertion sort algorithm.

    Args:
        arr: A list of comparable elements.

    Returns:
        None. The list is sorted in-place.
    """
    n = len(arr)  # Get the length of the array

    # Iterate through the array starting from the second element (index 1)
    for i in range(1, n):
        key = arr[i]  # The current element to be inserted into the sorted part
        j = i - 1    # Index of the last element in the sorted part

        # Move elements of arr[0..i-1] that are greater than key
        # to one position ahead of their current position
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]  # Shift the larger element to the right
            j -= 1              # Move to the next element in the sorted part

        # Insert the key into its correct position in the sorted part
        arr[j + 1] = key

def is_sorted(arr):
    """
    Checks if a list is sorted in non-decreasing order.

    Args:
        arr: A list of comparable elements.

    Returns:
        bool: True if the list is sorted, False otherwise.
    """
    return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))
