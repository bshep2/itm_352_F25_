def calculator():
    while True:  # Loop to allow multiple calculations
        try:
            num1 = float(input("Enter the first number: "))
            num2 = float(input("Enter the second number: "))
            operation = input("Choose an operation (add, subtract, multiply, divide) or type 'exit' to quit: ").strip().lower()

            if operation == 'exit':
                print("Exiting the calculator.")
                break  # Exit the loop if the user types 'exit'

            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                if num2 == 0:
                    return "Error: Division by zero is not allowed."
                result = num1 / num2
            else:
                return "Error: Invalid operation."

            print(f"The result is: {result}")

        except ValueError:
            print("Error: Invalid input. Please enter numeric values.")
        return "Error: Invalid input. Please enter numeric values."

print(calculator())