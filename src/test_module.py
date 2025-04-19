# Linear Search Function
def linear_search(arr, target):
    """
    This function performs a linear search on the given list.
    
    Parameters:
    arr (list): The list to search through.
    target (any): The value to find in the list.
    
    Returns:
    int: The index of the target element if found, otherwise -1.
    """
    # Loop through each element in the list using index
    for i in range(len(arr)):
        # Check if the current element is equal to the target
        if arr[i] == target:
            return i  # Return the index where the target is found

    return -1  # Target not found in the list

# Example usage
numbers = [5, 3, 7, 1, 9, 4]
target_value = 9

# Call the linear_search function
result = linear_search(numbers, target_value)

# Print the result
if result != -1:
    print(f"Target found at index {result}")
else:
    print("Target not found in the list")
