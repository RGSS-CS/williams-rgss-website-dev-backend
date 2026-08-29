import requests
from bs4 import BeautifulSoup

url = "https://drgwwilliams-ss.yrdsb.ca/"
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

school_name = soup.find(class_="top-nav-school-name").get_text()
school_phone = soup.find(class_="school_phn").get_text()
school_email = soup.find(class_="school_mail").get_text()

print(school_name, school_phone, school_email)