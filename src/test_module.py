 # Binary Search Function
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

# Example usage
sorted_numbers = [1, 3, 5, 7, 9, 11, 13,14]
target_value = 9

# Call the binary_search function
result = binary_search(sorted_numbers, target_value)

# Print the result
if result != -1:
    print(f"Target found at index {result}")
else:
    print("Target not found in the list")
