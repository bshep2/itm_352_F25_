import pandas as pd
import os 


current_dir = os.path.dirname(os.path.abspath(__file__))


sales_data_url = os.path.join(current_dir, 'sales_data.csv')

try:
    df - pd.read_csv(sales_data_url, on_bad_lines='skip')
