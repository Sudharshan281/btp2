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
