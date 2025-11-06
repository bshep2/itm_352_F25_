# Read the CSV file from the URL using exception handling and convert the data types using the pyarrow data type backend.
import pandas as pd

sales_data_url = 'https://drive.google.com/file/d/1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA/view?usp=sharing
try:
    df = pd.read_csv(sales_data_url, dtype_backend='pyarrow')
    print("Sales Data DataFrame:")
    print(df)
    print("\n")