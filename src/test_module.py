def ternary_search(arr, target):
    """
    Performs ternary search on a sorted array to find the target element.
    This is more efficient than binary search as it divides the search space into three parts.

    Args:
        arr: A sorted list or array of elements.
        target: The value to search for in the array.

    Returns:
        The index of the target element if found, otherwise -1.
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        # Calculate two mid points
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3

        # Check if target is at either mid point
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2

        # Update search space based on target's position
        if target < arr[mid1]:
            right = mid1 - 1
        elif target > arr[mid2]:
            left = mid2 + 1
        else:
            left = mid1 + 1
            right = mid2 - 1

    return -1  # Target not found

def merge_sort(arr):
    """
    Sorts a list using the merge sort algorithm.
    This is a divide-and-conquer algorithm that recursively splits the array
    into smaller subarrays until they are of size 1, then merges them back
    together in sorted order.

    Args:
        arr: A list of comparable elements.

    Returns:
        A new sorted list containing the elements from the input array.
    """
    if len(arr) <= 1:
        return arr

    # Divide the array into two halves
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    # Recursively sort the two halves
    left = merge_sort(left)
    right = merge_sort(right)

    # Merge the sorted halves
    return merge(left, right)

def merge(left, right):
    """
    Merges two sorted lists into a single sorted list.

    Args:
        left: A sorted list of comparable elements.
        right: A sorted list of comparable elements.

    Returns:
        A new sorted list containing all elements from both input lists.
    """
    result = []
    i = j = 0

    # Compare elements from both lists and merge them in sorted order
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add remaining elements from left list
    result.extend(left[i:])
    # Add remaining elements from right list
    result.extend(right[j:])

    return result

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
