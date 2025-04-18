"""
This module provides a binary search implementation.
"""

from typing import List, Optional

def binary_search(arr: List[int], target: int) -> Optional[int]:
    """
    Perform binary search on a sorted array to find the target value.
    
    Args:
        arr (List[int]): A sorted list of integers to search through.
        target (int): The value to search for.
        
    Returns:
        Optional[int]: The index of the target value if found, None otherwise.
        
    Raises:
        ValueError: If the input array is not sorted.
    """
    # Check if array is sorted
    if arr != sorted(arr):
        raise ValueError("Input array must be sorted")
        
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return None 