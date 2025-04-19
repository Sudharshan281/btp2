def binary_search(arr, target):
    """
    Performs binary search to find target element in a sorted array
    
    Args:
        arr: Sorted list of numbers
        target: Element to find
        
    Returns:
        Index of target if found, -1 if not found
    """
    # Initialize left and right pointers
    left = 0
    right = len(arr) - 1
    
    # Keep searching while valid search space exists
    while left <= right:
        # Find middle element
        mid = (left + right) // 2
        
        # If target found at mid, return index
        if arr[mid] == target:
            return mid
            
        # If target is greater, ignore left half
        elif arr[mid] < target:
            left = mid + 1
            
        # If target is smaller, ignore right half
        else:
            right = mid - 1
            
    # Target not found
    return -1