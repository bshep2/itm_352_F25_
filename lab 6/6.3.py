def test_determine_progress(progress_function):
    # Test case 1: spins = 0 -> should return "Get going!"
    assert progress_function(10, 0) == "Get going!", "Test case 1 failed"

    # Test case 2: hits/spins ratio <= 0 -> should return "Get going!"
    assert progress_function(0, 10) == "Get going!", "Test case 2 failed"
    assert progress_function(-1, 10) == "Get going!", "Test case 3 failed"

    # Test case 3: hits/spins ratio >= 0.5 but hits < spins -> "You win!"
    assert progress_function(4, 10) == "You win!", "Test case 4 failed"  # 0.4 ratio, hits < spins -> Not this case
    assert progress_function(5, 10) == "You win!", "Test case 5 failed"  # exactly 0.5 ratio and hits < spins
    assert progress_function(9, 10) == "You win!", "Test case 6 failed"  # >0.5 ratio and hits < spins

    # Test case 4: hits/spins ratio >= 0.25 but less than 0.5 -> "Almost there!"
    assert progress_function(3, 10) == "Almost there!", "Test case 7 failed"  # 0.3 ratio

    # Test case 5: hits/spins ratio > 0 and less than 0.25 -> "On your way!"
    assert progress_function(1, 10) == "On your way!", "Test case 8 failed"  # 0.1 ratio

    print("All test cases passed!")
