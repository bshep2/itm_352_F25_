import urllib.request
import ssl


# Ignore SSL certificate warnings (for HTTPS URLs)
ssl._create_default_https_context = ssl._create_unverified_context


# URL to fetch
url = "https://data.cityofchicago.org/Historic-Preservation/Landmark-Districts/zidz-sdfj/about_data"


# Open the URL
response = urllib.request.urlopen(url)


# Read the HTML content
html_content = response.readlines()


# Decode each line and print lines that contain <title> tags
for line in html_content:
   decoded_line = line.decode('utf-8')
   if '<title>' in decoded_line:
       print(decoded_line)
