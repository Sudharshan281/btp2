def insertion_sort(arr):
    # Iterate through the array starting from the second element
    for i in range(1, len(arr)):
        key = arr[i]  # The current element to be inserted
        j = i - 1     # Index of the previous element

        # Move elements of arr[0..i-1] that are greater than key
        # to one position ahead of their current position
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key  # Insert the key into its correct position