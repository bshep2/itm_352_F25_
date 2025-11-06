import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option("display.float_format", "${:,.2f}".format)
df = None

def load_data():
    global df
    df = pd.read_csv('https://raw.githubusercontent.com/bshep2/itm_352_F25_/main/assignment2_work/sales_data.csv')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales'] = df['quantity'] * df['unit_price']

def show_n():
    n = len(df)
    c = input(f"Rows (1-{n}, 'all', or Enter): ").strip()
    if c == '': return
    print(df if c == 'all' else df.head(int(c)) if 1 <= int(c) <= n else "Invalid")

def sr_type():
    print(pd.pivot_table(df, values='sales', index='region', columns='order_type', aggfunc='sum', margins=True))

def avg_region():
    print(pd.pivot_table(df, values='sales', index='region', columns='order_type', aggfunc='mean', margins=True))
    for r in df['region'].unique():
        d = df[df['region'] == r]
        s = d['state'].nunique()
        print(f"{r}: R=${d[d['order_type']=='Retail']['sales'].sum()/s:,.2f}/st W=${d[d['order_type']=='Wholesale']['sales'].sum()/s:,.2f}/st")

def cust_state():
    print(pd.pivot_table(df, values='sales', index=['state', 'customer_type'], columns='order_type', aggfunc='sum', fill_value=0))

def reg_prod():
    print(df.groupby(['region', 'product']).agg({'quantity': 'sum', 'sales': 'sum'}))

def cust():
    print(df.groupby('customer_type').agg({'quantity': 'sum', 'sales': 'sum'}))

def cat():
    print(df.groupby('category')['unit_price'].agg(['max', 'min']))

def emp():
    print(df.groupby('region')['employee_id'].nunique())

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
    
    print(pd.pivot_table(df, values=v[0] if len(v)==1 else v, index=r, columns=c, aggfunc=a[0] if len(a)==1 else a, margins=True))

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
    ("Exit", lambda: True)
)

def main():
    load_data()
    while True:
        print("\n--- Sales Dashboard ---")
        for i, (t, _) in enumerate(MENU, 1): print(f"{i}. {t}")
        try:
            if MENU[int(input("Choice: "))-1][1](): break
        except: pass
        input("Enter...")

if __name__ == "__main__": main()