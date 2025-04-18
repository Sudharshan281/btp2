def linear_search(arr: List[int], target: int) -> int:
    """
    Perform linear search on an array to find the target value.
    
    Args:
        arr (List[int]): A list of integers to search through.
        target (int): The value to search for.
        
    Returns:
        int: The index of the target value if found, -1 otherwise.
    """
    for index, value in enumerate(arr):
        if value == target:
            return index
    return -1
