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

def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        Average of the numbers
    """
    return sum(numbers) / len(numbers) if numbers else 0.0

def calculate_factorial(n: int) -> int:
    """Calculate the factorial of a number.
    
    Args:
        n: Number to calculate factorial of
        
    Returns:
        Factorial of n
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return 1 if n <= 1 else n * calculate_factorial(n - 1)

def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: Position in the Fibonacci sequence
        
    Returns:
        nth Fibonacci number
    """
    if n < 0:
        raise ValueError("Fibonacci sequence is not defined for negative numbers")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

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

class AdvancedCalculator(Calculator):
    """An advanced calculator that extends the basic calculator with more operations."""
    
    def power(self, x: float, y: float) -> float:
        """Calculate x raised to the power of y.
        
        Args:
            x: Base number
            y: Exponent
            
        Returns:
            x raised to the power of y
        """
        self.result = x ** y
        return self.result
        
    def square_root(self, x: float) -> float:
        """Calculate the square root of a number.
        
        Args:
            x: Number to find square root of
            
        Returns:
            Square root of x
        """
        self.result = x ** 0.5
        return self.result
        
    def factorial(self, x: int) -> int:
        """Calculate the factorial of a number.
        
        Args:
            x: Number to calculate factorial of
            
        Returns:
            Factorial of x
        """
        self.result = calculate_factorial(x)
        return self.result
        
    def fibonacci(self, n: int) -> int:
        """Calculate the nth Fibonacci number.
        
        Args:
            n: Position in the Fibonacci sequence
            
        Returns:
            nth Fibonacci number
        """
        self.result = calculate_fibonacci(n)
        return self.result 