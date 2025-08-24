
from typing import Union
from numbers import Number

__all__ = ["modable"]


def modable(n: Union[int, float], v: Union[int, float]) -> bool:
    """Check if n is divisible by v (i.e., n % v == 0).
    
    Args:
        n: The dividend (number to be divided)
        v: The divisor (number to divide by)
        
    Returns:
        bool: True if n is divisible by v, False otherwise
        
    Raises:
        ZeroDivisionError: If v is zero
        
    Examples:
        >>> modable(10, 2)
        True
        >>> modable(10, 3)
        False
        >>> modable(-10, 2)
        True
    """
    return n % v == 0
