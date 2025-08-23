def is_prime(n):
    """
    Check if a number is prime.
    
    Args:
        n (int): The number to check
        
    Returns:
        bool: True if n is prime, False otherwise
        
    Raises:
        ValueError: If n is not an integer
    """
    if not isinstance(n, int):
        raise ValueError("Input must be an integer")
    if n <= 1:
        return False
    if n == 2:
        return True
        
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True