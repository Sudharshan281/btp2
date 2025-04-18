"""
This module provides a simple random string generator.
"""

import random
import string

def generate_random_string(length: int = 10, include_digits: bool = True, include_special: bool = False) -> str:
    """
    Generate a random string of specified length.
    
    Args:
        length (int): The length of the random string to generate. Defaults to 10.
        include_digits (bool): Whether to include numbers in the string. Defaults to True.
        include_special (bool): Whether to include special characters. Defaults to False.
    
    Returns:
        str: A randomly generated string.
    
    Example:
        >>> generate_random_string(5, True, False)
        'a2b3c'
    """
    # Define character sets
    letters = string.ascii_letters
    digits = string.digits if include_digits else ''
    special_chars = string.punctuation if include_special else ''
    
    # Combine all allowed characters
    all_chars = letters + digits + special_chars
    
    # Generate random string
    return ''.join(random.choice(all_chars) for _ in range(length))

class RandomStringGenerator:
    """A class to generate random strings with various options."""
    
    def __init__(self, default_length: int = 10):
        """
        Initialize the RandomStringGenerator.
        
        Args:
            default_length (int): Default length for generated strings. Defaults to 10.
        """
        self.default_length = default_length
    
    def generate(self, length: int = None, uppercase_only: bool = False) -> str:
        """
        Generate a random string with specified options.
        
        Args:
            length (int, optional): Length of string to generate. Uses default_length if not specified.
            uppercase_only (bool): Whether to use only uppercase letters. Defaults to False.
        
        Returns:
            str: A randomly generated string.
        """
        actual_length = length if length is not None else self.default_length
        chars = string.ascii_uppercase if uppercase_only else string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(actual_length))

def calculate_factorial(n: int) -> int:
    """
    Calculate the factorial of a number.
    
    Args:
        n (int): The number to calculate factorial for.
        
    Returns:
        int: The factorial of the number.
        
    Raises:
        ValueError: If the input number is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1) 