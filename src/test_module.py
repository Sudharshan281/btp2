"""
Test module for documentation update workflow.
"""

import math

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

def calculate_gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Greatest common divisor of a and b
    """
    while b:
        a, b = b, a % b
    return abs(a)

def calculate_lcm(a: int, b: int) -> int:
    """
    Calculate the least common multiple (LCM) of two numbers.
    
    Args:
        a (int): First number
        b (int): Second number
        
    Returns:
        int: The least common multiple of a and b
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // calculate_gcd(a, b)

def calculate_absolute_difference(a: float, b: float) -> float:
    """
    Calculate the absolute difference between two numbers.
    
    Args:
        a (float): First number
        b (float): Second number
        
    Returns:
        float: Absolute difference between a and b
    """
    return abs(a - b)

def calculate_power(base: float, exponent: float) -> float:
    """
    Calculate the power of a number.
    
    Args:
        base (float): The base number
        exponent (float): The exponent to raise the base to
        
    Returns:
        float: The result of base raised to the power of exponent
    """
    return base ** exponent

def calculate_square_root(number: float) -> float:
    """
    Calculate the square root of a number.
    
    Args:
        number (float): The number to calculate the square root of
        
    Returns:
        float: The square root of the number
        
    Raises:
        ValueError: If the number is negative
    """
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return number ** 0.5

def calculate_cube(number: float) -> float:
    """
    Calculate the cube of a number.
    
    Args:
        number (float): The number to calculate the cube of
        
    Returns:
        float: The cube of the number
    """
    return number ** 3

def calculate_logarithm(number: float, base: float = 10.0) -> float:
    """
    Calculate the logarithm of a number with a specified base.
    
    Args:
        number (float): The number to calculate the logarithm of
        base (float, optional): The base of the logarithm. Defaults to 10.0.
        
    Returns:
        float: The logarithm of the number with the specified base
        
    Raises:
        ValueError: If the number is less than or equal to 0 or if the base is less than or equal to 0 or equal to 1
    """
    if number <= 0:
        raise ValueError("Cannot calculate logarithm of non-positive number")
    if base <= 0 or base == 1:
        raise ValueError("Base must be positive and not equal to 1")
    return math.log(number, base)

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
    
    def __init__(self):
        """Initialize the advanced calculator."""
        super().__init__()
        self.memory = 0
        
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
            
        Returns:
            float: Sum of a and b
        """
        self.result = a + b
        return self.result
        
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
            
        Returns:
            float: Difference of a and b
        """
        self.result = a - b
        return self.result
        
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
            
        Returns:
            float: Product of a and b
        """
        self.result = a * b
        return self.result
        
    def divide(self, a: float, b: float) -> float:
        """
        Divide two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
            
        Returns:
            float: Quotient of a and b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        self.result = a / b
        return self.result
        
    def power(self, base: float, exponent: float) -> float:
        """
        Calculate the power of a number.
        
        Args:
            base (float): The base number
            exponent (float): The exponent to raise the base to
            
        Returns:
            float: The result of base raised to the power of exponent
        """
        self.result = calculate_power(base, exponent)
        return self.result
        
    def square_root(self, number: float) -> float:
        """
        Calculate square root of a number.
        
        Args:
            number (float): Number to calculate square root of
            
        Returns:
            float: Square root of the number
            
        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        self.result = number ** 0.5
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
        
    def gcd(self, a: int, b: int) -> int:
        """
        Calculate Greatest Common Divisor (GCD) of two numbers.
        
        Args:
            a (int): First number
            b (int): Second number
            
        Returns:
            int: GCD of a and b
        """
        self.result = calculate_gcd(a, b)
        return self.result
        
    def lcm(self, a: int, b: int) -> int:
        """
        Calculate Least Common Multiple (LCM) of two numbers.
        
        Args:
            a (int): First number
            b (int): Second number
            
        Returns:
            int: LCM of a and b
        """
        self.result = calculate_lcm(a, b)
        return self.result

    def absolute_difference(self, a: float, b: float) -> float:
        """
        Calculate the absolute difference between two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
            
        Returns:
            float: Absolute difference between a and b
        """
        return calculate_absolute_difference(a, b) 