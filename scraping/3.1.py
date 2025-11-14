import requests
from bs4 import BeautifulSoup


# URL of the page with people data
url = "https://shidler.hawaii.edu/itm/people"


# Send a GET request to fetch the HTML content
response = requests.get(url)


# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')


# Use prettify() to print the first few lines of the parsed HTML
print(soup.prettify()[:500])  # Print the first 500 characters for brevity


# Find all people listed (you can adjust the tag and class based on the HTML structure)
people = soup.find_all('div', class_='views-field views-field-field-person-name')


# Extract names of people
people_names = [person.get_text(strip=True) for person in people]


# Print out the list of people and the number of people found
print("People List:")
print(people_names)
print(f"Total number of people: {len(people_names)}")
