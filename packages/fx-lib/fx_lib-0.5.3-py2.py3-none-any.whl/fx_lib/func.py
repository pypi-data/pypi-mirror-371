import math
from typing import Any, Callable, Iterator, List, Union
from numbers import Number

__all__ = ["range1", "enumerate1", "p", "convert_size", "chunks"]


def range1(n: int) -> range:
    """Create a 1-indexed range from 1 to n (inclusive).
    
    Args:
        n: The upper bound (inclusive)
        
    Returns:
        range: A range object from 1 to n+1
        
    Examples:
        >>> list(range1(5))
        [1, 2, 3, 4, 5]
        >>> list(range1(0))
        []
    """
    return range(1, n + 1)


def enumerate1(lst: Any) -> Iterator[tuple]:
    """Enumerate with 1-based indexing instead of 0-based.
    
    Args:
        lst: Any iterable object
        
    Returns:
        Iterator[tuple]: Enumerate object starting from index 1
        
    Examples:
        >>> list(enumerate1(['a', 'b', 'c']))
        [(1, 'a'), (2, 'b'), (3, 'c')]
    """
    return enumerate(lst, 1)


def p(current_value: Any, *args: Callable[[Any], Any]) -> Any:
    """Function composition utility - pipes value through functions.
    
    Args:
        current_value: Initial value to transform
        *args: Functions to apply in sequence
        
    Returns:
        Any: Result after applying all functions in sequence
        
    Examples:
        >>> p(5, lambda x: x * 2, lambda x: x + 3)
        13
        >>> p('hello', str.upper, lambda x: x + ' WORLD')
        'HELLO WORLD'
    """
    for func in args:
        current_value = func(current_value)
    return current_value


def convert_size(size: Union[int, float, str]) -> str:
    """Convert byte size to human readable format.
    
    Args:
        size: Size in bytes (can be int, float, or numeric string)
        
    Returns:
        str: Human readable size with appropriate unit
        
    Raises:
        ValueError: If size is negative or cannot be converted to number
        
    Examples:
        >>> convert_size(1024)
        '1.0KB'
        >>> convert_size(0)
        '0B'
        >>> convert_size(1536)
        '1.5KB'
    """
    try:
        size_bytes = int(size)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Size must be a valid number, got: {size}") from e
    
    if size_bytes < 0:
        raise ValueError(f"Size cannot be negative, got: {size_bytes}")
    
    if size_bytes == 0:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    _p = math.pow(1024, i)
    s = round(size_bytes / _p, 2)
    return f"{s}{size_name[i]}"


def chunks(lst: List[Any], n: int) -> Iterator[List[Any]]:
    """Split a list into evenly sized chunks.
    
    Args:
        lst: The list to split into chunks
        n: Size of each chunk (must be positive)
        
    Yields:
        List[Any]: Successive chunks of the input list
        
    Raises:
        ValueError: If chunk size is not positive
        
    Examples:
        >>> list(chunks([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
        >>> list(chunks([], 2))
        []
        
    References:
        https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks#answer-312464
    """
    if n <= 0:
        raise ValueError(f"Chunk size must be positive, got: {n}")
    
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
