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


def test_avg_abs():
    """Test function for avg_abs with various test cases."""
    
    def run_test(test_name, test_func):
        """Helper function to run a test and print results."""
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
    
    def test_positive_numbers():
        """Test with only positive numbers."""
        result = avg_abs(1, 2, 3, 4, 5)
        expected = 3.0
        return abs(result - expected) < 0.0001
    
    def test_negative_numbers():
        """Test with only negative numbers."""
        result = avg_abs(-1, -2, -3, -4, -5)
        expected = 3.0
        return abs(result - expected) < 0.0001
    
    def test_mixed_numbers():
        """Test with mixed positive and negative numbers."""
        result = avg_abs(-2, 4, -6, 8)
        expected = 5.0
        return abs(result - expected) < 0.0001
    
    def test_single_positive():
        """Test with single positive number."""
        result = avg_abs(7)
        expected = 7.0
        return abs(result - expected) < 0.0001
    
    def test_single_negative():
        """Test with single negative number."""
        result = avg_abs(-7)
        expected = 7.0
        return abs(result - expected) < 0.0001
    
    def test_with_zero():
        """Test with zero included."""
        result = avg_abs(0, 5, -5)
        expected = 10.0 / 3
        return abs(result - expected) < 0.0001
    
    def test_decimal_numbers():
        """Test with decimal numbers."""
        result = avg_abs(1.5, -2.5, 3.5, -4.5)
        expected = 3.0
        return abs(result - expected) < 0.0001
    
    def test_empty_input():
        """Test with no arguments - should raise ValueError."""
        try:
            avg_abs()
            return False  # Should not reach here
        except ValueError:
            return True
        except:
            return False
    
    def test_large_numbers():
        """Test with large numbers."""
        result = avg_abs(1000, -2000, 3000, -4000)
        expected = 2500.0
        return abs(result - expected) < 0.0001
    
    # Run all tests
    print("Running tests for avg_abs function:")
    print("=" * 40)
    
    run_test("Positive numbers only", test_positive_numbers)
    run_test("Negative numbers only", test_negative_numbers)
    run_test("Mixed positive/negative", test_mixed_numbers)
    run_test("Single positive number", test_single_positive)
    run_test("Single negative number", test_single_negative)
    run_test("Numbers with zero", test_with_zero)
    run_test("Decimal numbers", test_decimal_numbers)
    run_test("Empty input (error case)", test_empty_input)
    run_test("Large numbers", test_large_numbers)
    
    print("=" * 40)
    print("Test execution completed!")


if __name__ == "__main__":
    # Run the tests when the script is executed directly
    test_avg_abs()