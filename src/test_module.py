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
