import requests
import pandas as pd


# URL to fetch the driver type data
url = "https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type"


# Make a GET request to the API
response = requests.get(url)


# Convert the response to JSON
data = response.json()


# Convert the JSON data into a pandas DataFrame
df = pd.DataFrame(data)


# Set columns and index
df = df[['driver_type', 'count_license']]
df.set_index('driver_type', inplace=True)


# Print out the DataFrame
print(df)
