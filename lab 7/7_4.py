recent_purchases = [36.13, 23.87, 183.35, 22.93, 11.62]
budget = 50.00

for expense in recent_purchases:
    if expense > budget:
        print("This purchase is over budget!")
    else:
        print("This purchase is within budget")