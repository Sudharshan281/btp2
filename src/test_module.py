"""
Test module for documentation update workflow.
"""

def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Product of a and b
    """
    return a * b

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.result = 0
        
    def add(self, x: int, y: int) -> int:
        """Add two numbers.
        
        Args:
            x: First number
            y: Second number
            
        Returns:
            Sum of x and y
        """
        self.result = x + y
        return self.result
        
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers.
        
        Args:
            x: First number
            y: Second number
            
        Returns:
            Product of x and y
        """
        self.result = x * y
        return self.result 