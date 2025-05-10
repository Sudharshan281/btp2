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

def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): The position in the Fibonacci sequence (0-based)
        
    Returns:
        int: The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def calculate_power(base: float, exponent: float) -> float:
    """
    Calculate the power of a number.
    
    Args:
        base (float): The base number
        exponent (float): The exponent
        
    Returns:
        float: The result of base raised to the power of exponent
    """
    return base ** exponent

def calculate_factorial(n: int) -> int:
    """
    Calculate the factorial of a number.
    
    Args:
        n (int): The number to calculate factorial for
        
    Returns:
        int: The factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)

# Example usage
sorted_numbers = [1, 3, 5, 7, 9, 11, 13]
target = 7
result = binary_search(sorted_numbers, target)
print(f"Found {target} at index {result}")  # Output: Found 7 at index 3
