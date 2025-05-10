def binary_search(arr, target):
    """
    Performs binary search on a sorted list to find the target element.

    Parameters:
    arr (list): A sorted list to search.
    target (any): The value to search for.

    Returns:
    int: The index of the target if found, otherwise -1.
    """
    # Set the initial left and right boundaries
    left = 0
    right = len(arr) - 1

    # Loop until the search space is exhausted
    while left <= right:
        # Calculate the middle index
        mid = (left + right) // 2

        # Check if the middle element is the target
        if arr[mid] == target:
            return mid  # Target found at index mid
        elif arr[mid] < target:
            # If the target is greater, ignore the left half
            left = mid + 1
        else:
            # If the target is smaller, ignore the right half
            right = mid - 1

    return -1  # Target not found

def linear_search(arr, target):
    """
    Performs linear search on a list to find the target element.

    Parameters:
    arr (list): The list to search.
    target (any): The value to search for.

    Returns:
    int: The index of the target if found, otherwise -1.
    """
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1