"""
Test API module for documentation testing.
"""

def calculate_sum(a: int, b: int) -> int:
    """
    Calculate the sum of two integers.
    
    Args:
        a (int): First number
        b (int): Second number
        
    Returns:
        int: Sum of a and b
    """
    return a + b

def calculate_product(a: int, b: int) -> int:
    """
    Calculate the product of two integers.
    
    Args:
        a (int): First number
        b (int): Second number
        
    Returns:
        int: Product of a and b
    """
    return a * b

def calculate_power(base: int, exponent: int) -> int:
    """
    Calculate the power of a number.
    
    Args:
        base (int): The base number
        exponent (int): The exponent
        
    Returns:
        int: base raised to the power of exponent
    """
    return base ** exponent

def calculate_factorial(n: int) -> int:
    """
    Calculate the factorial of a number.
    
    Args:
        n (int): The number to calculate factorial for
        
    Returns:
        int: Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)

class MathOperations:
    """
    A class for performing mathematical operations.
    """
    
    def __init__(self):
        """Initialize the MathOperations class."""
        pass
    
    def divide(self, a: int, b: int) -> float:
        """
        Divide two numbers.
        
        Args:
            a (int): Dividend
            b (int): Divisor
            
        Returns:
            float: Result of division
            
        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b 