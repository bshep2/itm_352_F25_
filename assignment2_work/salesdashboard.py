import pandas as pd
import os 


current_dir = os.path.dirname(os.path.abspath(__file__))


sales_data_path = os.path.join(current_dir, 'sales_data.csv')

try:
    #Using 
    df - pd.read_csv(sales_data_url, on_bad_lines='skip')