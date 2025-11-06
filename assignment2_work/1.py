import pandas as pd
import ssl
import urllib.request

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

sales_data_url = 'https://raw.githubusercontent.com/bshep2/itm_352_F25_/main/assignment2_work/sales_data.csv'

try:
    df = pd.read_csv(sales_data_url, on_bad_lines='skip')
    print("Data loaded successfully")
    print(df.head())
except Exception as e:
    print(f"An error occurred: {e}")