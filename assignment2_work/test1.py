import pandas as pd
import ssl

# had to disable ssl to load from github
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option("display.float_format", "${:,.2f}".format)

df = None
saved_results = {}  # store all the analysis results

def load_data():
    global df
    url = 'https://raw.githubusercontent.com/bshep2/itm_352_F25_/main/assignment2_work/sales_data.csv'
    df = pd.read_csv(url)
    # convert these to numbers in case they're strings
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales'] = df['quantity'] * df['unit_price']  # calculate total sales
    print("Data loaded successfully!")

def export_result(data, analysis_name):
    # ask if user wants excel file
    export = input("\nExport to Excel? (y/n): ")
    if export == 'y' or export == 'Y':
        filename = input("Enter filename (without .xlsx): ")
        if filename == '':
            filename = analysis_name
        try:
            data.to_excel(filename + ".xlsx")
            print(f"File saved: {filename}.xlsx")
        except:
            print("Error saving file")

def show_first_rows():
    total = len(df)
    print(f"\nTotal rows in dataset: {total}")
    user_choice = input(f"How many rows? (1-{total}, 'all', or Enter to skip): ")
    
    if user_choice == '':
        print("Skipped")
        return
    
    if user_choice == 'all':
        data = df
    else:
        num = int(user_choice)
        data = df.head(num)
    
    print(data)
    saved_results["First_rows"] = data
    export_result(data, "First_rows")

def total_sales_region_ordertype():
    # pivot table - sales by region with retail/wholesale columns
    pivot = pd.pivot_table(df, values='sales', index='region', 
                          columns='order_type', aggfunc='sum', margins=True)
    print("\nTotal Sales by Region and Order Type:")
    print(pivot)
    saved_results["Sales_by_region_ordertype"] = pivot
    export_result(pivot, "Sales_by_region_ordertype")

def avg_sales_by_region():
    # calculate averages
    pivot = pd.pivot_table(df, values='sales', index='region', 
                          columns='order_type', aggfunc='mean', margins=True)
    print("\nAverage Sales by Region and Order Type:")
    print(pivot)
    
    # also show average per state in each region
    print("\nAverage per state:")
    regions = df['region'].unique()
    for region in regions:
        region_df = df[df['region'] == region]
        num_states = region_df['state'].nunique()
        
        retail_sales = region_df[region_df['order_type']=='Retail']['sales'].sum()
        wholesale_sales = region_df[region_df['order_type']=='Wholesale']['sales'].sum()
        
        retail_avg = retail_sales / num_states
        wholesale_avg = wholesale_sales / num_states
        print(f"{region}: Retail=${retail_avg:,.2f}/state, Wholesale=${wholesale_avg:,.2f}/state")
    
    saved_results["Avg_sales_region"] = pivot
    export_result(pivot, "Avg_sales_region")

def sales_customer_state():
    # group by state and customer type
    pivot = pd.pivot_table(df, values='sales', 
                          index=['state','customer_type'], 
                          columns='order_type', aggfunc='sum', fill_value=0)
    print("\nSales by Customer Type and Order Type (by State):")
    print(pivot)
    saved_results["Sales_customer_state"] = pivot
    export_result(pivot, "Sales_customer_state")

def sales_region_product():
    grouped = df.groupby(['region','product']).agg({'quantity':'sum','sales':'sum'})
    print("\nQuantity and Sales by Region and Product:")
    print(grouped)
    saved_results["Sales_region_product"] = grouped
    export_result(grouped, "Sales_region_product")

def sales_by_customer():
    grouped = df.groupby('customer_type').agg({'quantity':'sum','sales':'sum'})
    print("\nQuantity and Sales by Customer Type:")
    print(grouped)
    saved_results["Sales_by_customer"] = grouped
    export_result(grouped, "Sales_by_customer")

def max_min_price_category():
    stats = df.groupby('category')['unit_price'].agg(['max','min'])
    print("\nMax and Min Prices by Category:")
    print(stats)
    saved_results["Price_by_category"] = stats
    export_result(stats, "Price_by_category")

def unique_employees():
    counts = df.groupby('region')['employee_id'].nunique()
    print("\nNumber of Unique Employees by Region:")
    print(counts)
    saved_results["Employees_by_region"] = counts
    export_result(counts, "Employees_by_region")

def build_custom_pivot():
    print("\n=== Build Custom Pivot Table ===")
    
    # options
    row_options = ['employee_name','sales_region','product_category','region','state','category','product']
    col_options = ['order_type','customer_type']
    value_options = ['quantity','sales','unit_price']
    agg_options = ['sum','mean','count']
    
    # user picks rows
    print("\nChoose row field(s):")
    for i in range(len(row_options)):
        print(f"  {i+1}. {row_options[i]}")
    row_input = input("Enter number(s) separated by commas: ")
    row_choices = []
    for num in row_input.split(','):
        idx = int(num) - 1
        row_choices.append(row_options[idx])
    
    # user picks columns (optional)
    print("\nChoose column field(s) - optional:")
    for i in range(len(col_options)):
        print(f"  {i+1}. {col_options[i]}")
    col_input = input("Enter number(s) separated by commas (or Enter for none): ")
    
    if col_input == '':
        col_choices = None
    else:
        col_choices = []
        for num in col_input.split(','):
            idx = int(num) - 1
            col_choices.append(col_options[idx])
    
    # user picks values
    print("\nChoose value field(s):")
    for i in range(len(value_options)):
        print(f"  {i+1}. {value_options[i]}")
    val_input = input("Enter number(s) separated by commas: ")
    val_choices = []
    for num in val_input.split(','):
        idx = int(num) - 1
        val_choices.append(value_options[idx])
    
    # user picks aggregation
    print("\nChoose aggregation function(s):")
    for i in range(len(agg_options)):
        print(f"  {i+1}. {agg_options[i]}")
    agg_input = input("Enter number(s) separated by commas: ")
    agg_choices = []
    for num in agg_input.split(','):
        idx = int(num) - 1
        agg_choices.append(agg_options[idx])
    
    # create the pivot
    # if only one value/agg, use string instead of list
    values_to_use = val_choices[0] if len(val_choices) == 1 else val_choices
    agg_to_use = agg_choices[0] if len(agg_choices) == 1 else agg_choices
    
    pivot = pd.pivot_table(df, values=values_to_use, index=row_choices, 
                          columns=col_choices, aggfunc=agg_to_use, margins=True)
    
    print("\n=== Your Custom Pivot Table ===")
    print(pivot)
    
    name = "Custom_pivot_" + "_".join(row_choices)
    saved_results[name] = pivot
    export_result(pivot, name)

def show_saved_results():
    if len(saved_results) == 0:
        print("\nNo saved results yet!")
        return
    
    print("\n========== All Saved Results ==========")
    count = 1
    for name in saved_results:
        print(f"\n--- Result {count}: {name} ---")
        print(saved_results[name])
        count = count + 1

def exit_dashboard():
    print("\nThanks for using the dashboard!")
    return True

# menu - tuple with menu text and function
menu_items = (
    ("Show the first n rows of sales data", show_first_rows),
    ("Total sales by region and order_type", total_sales_region_ordertype),
    ("Average sales by region with average sales by state and sale type", avg_sales_by_region),
    ("Sales by customer type and order type by state", sales_customer_state),
    ("Total sales quantity and price by region and product", sales_region_product),
    ("Total sales quantity and price customer type", sales_by_customer),
    ("Max and min sales price of sales by category", max_min_price_category),
    ("Number of unique employees by region", unique_employees),
    ("Create a custom pivot table", build_custom_pivot),
    ("Show all saved results", show_saved_results),
    ("Exit", exit_dashboard)
)

def main():
    print("Welcome to Sales Data Dashboard")
    load_data()
    
    # main loop
    while True:
        # display saved results if any
        if len(saved_results) > 0:
            print("\n========== Saved Results ==========")
            counter = 1
            for result_name in saved_results:
                print(f"  {counter}. {result_name}")
                counter = counter + 1
        
        # display menu
        print("\n--- Sales Data Dashboard ---")
        menu_num = 1
        for item in menu_items:
            menu_text = item[0]
            print(f"{menu_num}. {menu_text}")
            menu_num = menu_num + 1
        
        # get user choice
        user_input = input("\nEnter your choice: ")
        
        try:
            choice = int(user_input)
            
            if choice < 1 or choice > len(menu_items):
                print(f"Please enter a number between 1 and {len(menu_items)}")
                input("\nPress Enter to continue...")
                continue
            
            # run the selected function
            selected_item = menu_items[choice - 1]
            selected_function = selected_item[1]
            should_exit = selected_function()
            
            if should_exit == True:
                break
            
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as error:
            print(f"Error: {error}")
        
        input("\nPress Enter to continue...")

# run program
if __name__ == "__main__":
    main()