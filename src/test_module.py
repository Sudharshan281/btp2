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

def ternary_search(arr: List[int], target: int) -> int:
    """
    Perform ternary search on a sorted array to find the target value.
    
    Args:
        arr (List[int]): A sorted list of integers to search in
        target (int): The value to search for
        
    Returns:
        int: The index of the target value if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        # Calculate two mid points
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3
        
        # Check if target is at either mid point
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2
            
        # If target is in left third
        if target < arr[mid1]:
            right = mid1 - 1
        # If target is in right third
        elif target > arr[mid2]:
            left = mid2 + 1
        # If target is in middle third
        else:
            left = mid1 + 1
            right = mid2 - 1
            
    return -1 