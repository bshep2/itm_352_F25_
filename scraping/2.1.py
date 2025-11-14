import pandas as pd
import ssl


# Ignore SSL certificate warnings (for HTTPS URLs)
ssl._create_default_https_context = ssl._create_unverified_context


# URL to fetch the interest rate table
url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202410"


# Use pandas to read the HTML table(s) into a list of DataFrames
dfs = pd.read_html(url)


# The table we are interested in is the first table on the page
interest_rate_df = dfs[0]


# Print out the columns
print(interest_rate_df.columns)


# Loop through the rows and print the 1 month interest rates
for index, row in interest_rate_df.iterrows():
   print(f"1 Mo Interest Rate: {row['1 Mo']}")


