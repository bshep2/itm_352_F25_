import requests
from bs4 import BeautifulSoup


# URL of the mortgage rate page
url = "https://www.hicentral.com/hawaii-mortgage-rates.php"


# Send a GET request to fetch the page content
response = requests.get(url)


# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')


# Find the mortgage rate table (you may need to adjust the tag and class)
table = soup.find('table', {'class': 'tablepress'})


# Extract rows from the table
rows = table.find_all('tr')


# Loop through the rows and extract the bank name and rate
for row in rows[1:]:  # Skip header row
   cols = row.find_all('td')
   bank_name = cols[0].text.strip()
   rate = cols[1].text.strip()
   print(f"Bank: {bank_name}, Rate: {rate}")
