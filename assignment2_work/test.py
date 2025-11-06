import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option("display.float_format", "${:,.2f}".format)
df = None
results = {}

def load_data():
    global df
    df = pd.read_csv('https://raw.githubusercontent.com/bshep2/itm_352_F25_/main/assignment2_work/sales_data.csv')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales'] = df['quantity'] * df['unit_price']

def save_result(name, result):
    results[name] = result
    if input("\nExport to Excel? (y/n): ").lower() == 'y':
        fname = input("Filename (without .xlsx): ") + ".xlsx"
        result.to_excel(fname)
        print(f"Saved to {fname}")

def show_n():
    n = len(df)
    c = input(f"Rows (1-{n}, 'all', or Enter): ").strip()
    if c == '': return
    r = df if c == 'all' else df.head(int(c)) if 1 <= int(c) <= n else "Invalid"
    print(r)
    save_result("First n rows", r)

def sr_type():
    r = pd.pivot_table(df, values='sales', index='region', columns='order_type', aggfunc='sum', margins=True)
    print(r)
    save_result("Sales by region/type", r)

def avg_region():
    r = pd.pivot_table(df, values='sales', index='region', columns='order_type', aggfunc='mean', margins=True)
    print(r)
    for reg in df['region'].unique():
        d = df[df['region'] == reg]
        s = d['state'].nunique()
        print(f"{reg}: R=${d[d['order_type']=='Retail']['sales'].sum()/s:,.2f}/st W=${d[d['order_type']=='Wholesale']['sales'].sum()/s:,.2f}/st")
    save_result("Avg sales by region", r)

def cust_state():
    r = pd.pivot_table(df, values='sales', index=['state', 'customer_type'], columns='order_type', aggfunc='sum', fill_value=0)
    print(r)
    save_result("Sales by customer/state", r)

def reg_prod():
    r = df.groupby(['region', 'product']).agg({'quantity': 'sum', 'sales': 'sum'})
    print(r)
    save_result("Sales by region/product", r)

def cust():
    r = df.groupby('customer_type').agg({'quantity': 'sum', 'sales': 'sum'})
    print(r)
    save_result("Sales by customer", r)

def cat():
    r = df.groupby('category')['unit_price'].agg(['max', 'min'])
    print(r)
    save_result("Price by category", r)

def emp():
    r = df.groupby('region')['employee_id'].nunique()
    print(r)
    save_result("Employees by region", r)

def custom():
    ro = ['employee_name', 'sales_region', 'product_category', 'region', 'state', 'category', 'product']
    co = ['order_type', 'customer_type']
    vo = ['quantity', 'sales', 'unit_price']
    ao = ['sum', 'mean', 'count']
    
    print("\nRows:", *[f"{i}.{o}" for i,o in enumerate(ro,1)])
    r = [ro[int(i)-1] for i in input("Pick: ").split(',')]
    print("Cols:", *[f"{i}.{o}" for i,o in enumerate(co,1)])
    c = input("Pick (or Enter): ")
    c = [co[int(i)-1] for i in c.split(',')] if c else None
    print("Values:", *[f"{i}.{o}" for i,o in enumerate(vo,1)])
    v = [vo[int(i)-1] for i in input("Pick: ").split(',')]
    print("Agg:", *[f"{i}.{o}" for i,o in enumerate(ao,1)])
    a = [ao[int(i)-1] for i in input("Pick: ").split(',')]
    
    result = pd.pivot_table(df, values=v[0] if len(v)==1 else v, index=r, columns=c, aggfunc=a[0] if len(a)==1 else a, margins=True)
    print(result)
    save_result(f"Custom pivot ({','.join(r)})", result)

def show_all():
    if not results:
        print("\nNo results stored yet.")
        return
    print("\n=== All Stored Results ===")
    for i, (name, result) in enumerate(results.items(), 1):
        print(f"\n{i}. {name}")
        print(result)

MENU = (
    ("Show first n rows", show_n),
    ("Total sales by region/order_type", sr_type),
    ("Avg sales by region", avg_region),
    ("Sales by customer/order/state", cust_state),
    ("Sales by region/product", reg_prod),
    ("Sales by customer type", cust),
    ("Max/min price by category", cat),
    ("Unique employees by region", emp),
    ("Custom pivot", custom),
    ("Show all stored results", show_all),
    ("Exit", lambda: True)
)

def main():
    load_data()
    while True:
        if results:
            print("\n=== Stored Results ===")
            for i, name in enumerate(results.keys(), 1):
                print(f"{i}. {name}")
        
        print("\n--- Sales Dashboard ---")
        for i, (t, _) in enumerate(MENU, 1): print(f"{i}. {t}")
        try:
            if MENU[int(input("Choice: "))-1][1](): break
        except: pass
        input("\nEnter...")

if __name__ == "__main__": main()