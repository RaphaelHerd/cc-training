def avg_abs(*numbers):
    """
    Calculate the average of absolute values of the given numbers.
    
    Args:
        *numbers: Variable number of numeric arguments
        
    Returns:
        float: The average of absolute values
        
    Raises:
        ValueError: If no numbers are provided
    """
    # We expect the array to be non-null and non-empty
    if not numbers or len(numbers) == 0:
        raise ValueError("Array numbers must not be null or empty!")
    
    total_sum = 0
    for num in numbers:
        if num < 0:
            total_sum -= num  # This makes negative numbers positive (absolute value)
        else:
            total_sum += num
    
    return total_sum / len(numbers)