recent_purchases = [36.13, 23.87, 183.35, 22.93, 11.62]
budget = 50.00

for expense in recent_purchases:
    if expense > budget:
        print("This purchase is over budget!")
    else:
        print("This purchase is within budget")
        def check_budget(expenses, budget):
            results = []
            for expense in expenses:
                if expense > budget:
                    results.append("This purchase is over budget!")
                else:
                    results.append("This purchase is within budget")
            return results

        # Test cases
        def test_check_budget():
            assert check_budget([36.13, 23.87, 183.35, 22.93, 11.62], 50.00) == [
                "This purchase is within budget",
                "This purchase is within budget",
                "This purchase is over budget!",
                "This purchase is within budget",
                "This purchase is within budget"
            ]
            assert check_budget([100.00, 50.00, 25.00], 75.00) == [
                "This purchase is over budget!",
                "This purchase is over budget!",
                "This purchase is within budget"
            ]
            assert check_budget([], 50.00) == []

        # Call the test function
        test_check_budget()