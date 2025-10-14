for number in range(1, 11):
    if number == 5:
        continue
    if number == 8:
        print("Reached 8, stopping the loop.")
        break
    print(number)