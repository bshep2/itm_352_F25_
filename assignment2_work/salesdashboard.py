import pandas as pd
import ssl
import os

# Disable SSL to load from github
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option("display.float_format", "${:,.2f}".format)

df = None
saved_results = {}

def load_data():
    """Load sales data from CSV file"""
    global df
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'sales_data.csv')
    
    df = pd.read_csv(file_path)
    
    # Convert to numbers in case they're strings
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales'] = df['quantity'] * df['unit_price']
    
    print("Data loaded successfully!")
    print(f"Total rows: {len(df)}")

def export_result(data, analysis_name):
    """Ask user if they want to export results to Excel"""
    export = input("\nExport to Excel? (y/n): ")
    if export.lower() == 'y':
        filename = input("Enter filename (without .xlsx): ")
        if filename == '':
            filename = analysis_name
        try:
            data.to_excel(filename + ".xlsx")
            print(f"File saved: {filename}.xlsx")
        except Exception as e:
            print(f"Error saving file: {e}")

def show_first_rows():
    """Display first n rows of the dataset"""
    total = len(df)
    print(f"\nTotal rows in dataset: {total}")
    user_choice = input(f"How many rows to display? (1-{total}, 'all', or Enter to skip): ")
    
    if user_choice == '':
        print("Skipped")
        return
    
    if user_choice.lower() == 'all':
        data = df
    else:
        try:
            num = int(user_choice)
            data = df.head(num)
        except ValueError:
            print("Invalid input")
            return
    
    print(data)
    saved_results["First_rows"] = data
    export_result(data, "First_rows")

def total_sales_region_ordertype():
    """Calculate total sales by region and order type"""
    pivot = pd.pivot_table(df, values='sales', index='sales_region', 
                          columns='order_type', aggfunc='sum', margins=True)
    print("\nTotal Sales by Region and Order Type:")
    print(pivot)
    saved_results["Sales_by_region_ordertype"] = pivot
    export_result(pivot, "Sales_by_region_ordertype")

def avg_sales_by_region():
    """Calculate average sales by region and order type"""
    pivot = pd.pivot_table(df, values='sales', index='sales_region', 
                          columns='order_type', aggfunc='mean', margins=True)
    print("\nAverage Sales by Region and Order Type:")
    print(pivot)
    
    # Calculate average per state
    print("\nAverage per state:")
    regions = df['sales_region'].unique()
    for region in regions:
        region_data = df[df['sales_region'] == region]
        num_states = region_data['customer_state'].nunique()
        
        retail_sales = region_data[region_data['order_type']=='Retail']['sales'].sum()
        wholesale_sales = region_data[region_data['order_type']=='Wholesale']['sales'].sum()
        
        retail_avg = retail_sales / num_states
        wholesale_avg = wholesale_sales / num_states
        print(f"{region}: Retail=${retail_avg:,.2f}/state, Wholesale=${wholesale_avg:,.2f}/state")
    
    saved_results["Avg_sales_region"] = pivot
    export_result(pivot, "Avg_sales_region")

def sales_customer_state():
    """Calculate sales by customer type and order type for each state"""
    pivot = pd.pivot_table(df, values='sales', 
                          index=['customer_state','customer_type'], 
                          columns='order_type', aggfunc='sum', fill_value=0)
    print("\nSales by Customer Type and Order Type (by State):")
    print(pivot)
    saved_results["Sales_customer_state"] = pivot
    export_result(pivot, "Sales_customer_state")

def sales_region_product():
    """Calculate quantity and sales by region and product"""
    grouped = df.groupby(['sales_region','produce_name']).agg({'quantity':'sum','sales':'sum'})
    print("\nQuantity and Sales by Region and Product:")
    print(grouped)
    saved_results["Sales_region_product"] = grouped
    export_result(grouped, "Sales_region_product")

def sales_by_customer():
    """Calculate quantity and sales by customer type"""
    grouped = df.groupby('customer_type').agg({'quantity':'sum','sales':'sum'})
    print("\nQuantity and Sales by Customer Type:")
    print(grouped)
    saved_results["Sales_by_customer"] = grouped
    export_result(grouped, "Sales_by_customer")

def max_min_price_category():
    """Find max and min prices by product category"""
    stats = df.groupby('product_category')['unit_price'].agg(['max','min'])
    print("\nMax and Min Prices by Category:")
    print(stats)
    saved_results["Price_by_category"] = stats
    export_result(stats, "Price_by_category")

def unique_employees():
    """Count unique employees by region"""
    counts = df.groupby('sales_region')['employee_id'].nunique()
    print("\nNumber of Unique Employees by Region:")
    print(counts)
    saved_results["Employees_by_region"] = counts
    export_result(counts, "Employees_by_region")

def build_custom_pivot():
    """Interactive custom pivot table builder"""
    print("\n=== Build Custom Pivot Table ===")
    
    # Row field selection
    print("\nChoose row field(s):")
    print("  1. employee_name")
    print("  2. sales_region")
    print("  3. product_category")
    print("  4. customer_state")
    print("  5. job_title")
    print("  6. produce_name")
    row_input = input("Enter number(s) separated by commas: ")
    
    row_options = ['employee_name','sales_region','product_category','customer_state','job_title','produce_name']
    row_choices = []
    for num in row_input.split(','):
        try:
            idx = int(num.strip()) - 1
            row_choices.append(row_options[idx])
        except (ValueError, IndexError):
            print(f"Invalid choice: {num}")
            return
    
    # Column field selection (optional)
    print("\nChoose column field(s) - optional:")
    print("  1. order_type")
    print("  2. customer_type")
    col_input = input("Enter number(s) separated by commas (or Enter for none): ")
    
    col_options = ['order_type','customer_type']
    if col_input.strip() == '':
        col_choices = None
    else:
        col_choices = []
        for num in col_input.split(','):
            try:
                idx = int(num.strip()) - 1
                col_choices.append(col_options[idx])
            except (ValueError, IndexError):
                print(f"Invalid choice: {num}")
                return
    
    # Value field selection
    print("\nChoose value field(s):")
    print("  1. quantity")
    print("  2. sales")
    print("  3. unit_price")
    val_input = input("Enter number(s) separated by commas: ")
    
    value_options = ['quantity','sales','unit_price']
    val_choices = []
    for num in val_input.split(','):
        try:
            idx = int(num.strip()) - 1
            val_choices.append(value_options[idx])
        except (ValueError, IndexError):
            print(f"Invalid choice: {num}")
            return
    
    # Aggregation function selection
    print("\nChoose aggregation function(s):")
    print("  1. sum")
    print("  2. mean")
    print("  3. count")
    agg_input = input("Enter number(s) separated by commas: ")
    
    agg_options = ['sum','mean','count']
    agg_choices = []
    for num in agg_input.split(','):
        try:
            idx = int(num.strip()) - 1
            agg_choices.append(agg_options[idx])
        except (ValueError, IndexError):
            print(f"Invalid choice: {num}")
            return
    
    # Create pivot table
    values_to_use = val_choices[0] if len(val_choices) == 1 else val_choices
    agg_to_use = agg_choices[0] if len(agg_choices) == 1 else agg_choices
    
    try:
        pivot = pd.pivot_table(df, values=values_to_use, index=row_choices, 
                              columns=col_choices, aggfunc=agg_to_use, margins=True)
        
        print("\n=== Your Custom Pivot Table ===")
        print(pivot)
        
        name = "Custom_pivot_" + "_".join(row_choices)
        saved_results[name] = pivot
        export_result(pivot, name)
    except Exception as e:
        print(f"Error creating pivot table: {e}")

def show_saved_results():
    """Display all previously saved analysis results"""
    if len(saved_results) == 0:
        print("\nNo saved results yet!")
        return
    
    print("\n========== All Saved Results ==========")
    count = 1
    for name in saved_results:
        print(f"\n--- Result {count}: {name} ---")
        print(saved_results[name])
        count += 1

def exit_dashboard():
    """Exit the application"""
    print("\nThanks for using the dashboard!")
    return True

def main():
    """Main program loop"""
    print("=" * 50)
    print("Welcome to Sales Data Dashboard")
    print("=" * 50)
    
    # Load data at startup
    try:
        load_data()
    except FileNotFoundError:
        print("Error: sales_data.csv not found in current directory")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Main menu loop
    while True:
        # Display saved results if any exist
        if len(saved_results) > 0:
            print("\n========== Saved Results ==========")
            counter = 1
            for result_name in saved_results:
                print(f"  {counter}. {result_name}")
                counter += 1
        
        # Display menu options
        print("\n" + "=" * 50)
        print("Sales Data Dashboard Menu")
        print("=" * 50)
        print("1. Show the first n rows of sales data")
        print("2. Total sales by region and order_type")
        print("3. Average sales by region with average sales by state and sale type")
        print("4. Sales by customer type and order type by state")
        print("5. Total sales quantity and price by region and product")
        print("6. Total sales quantity and price customer type")
        print("7. Max and min sales price of sales by category")
        print("8. Number of unique employees by region")
        print("9. Create a custom pivot table")
        print("10. Show all saved results")
        print("11. Exit")
        print("=" * 50)
        
        # Get user input
        user_input = input("\nEnter your choice (1-11): ")
        
        try:
            choice = int(user_input)
            
            # Validate choice range
            if choice < 1 or choice > 11:
                print("Please enter a number between 1 and 11")
                input("\nPress Enter to continue...")
                continue
            
            # Execute selected function
            try:
                if choice == 1:
                    show_first_rows()
                elif choice == 2:
                    total_sales_region_ordertype()
                elif choice == 3:
                    avg_sales_by_region()
                elif choice == 4:
                    sales_customer_state()
                elif choice == 5:
                    sales_region_product()
                elif choice == 6:
                    sales_by_customer()
                elif choice == 7:
                    max_min_price_category()
                elif choice == 8:
                    unique_employees()
                elif choice == 9:
                    build_custom_pivot()
                elif choice == 10:
                    show_saved_results()
                elif choice == 11:
                    exit_dashboard()
                    break
            except KeyError as e:
                print(f"\nError: Column {e} not found in data")
            except Exception as e:
                print(f"Error during analysis: {e}")
            
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 11.")
        
        input("\nPress Enter to continue...")

# Run the program
if __name__ == "__main__":
    main()