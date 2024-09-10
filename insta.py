import requests
from bs4 import BeautifulSoup

# Function to fetch Instagram page and parse it
def fetch_instagram_data(username):
    url = f"https://www.instagram.com/{username}/following/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url} with status code {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all div elements with class x1dm5mii
    div_elements = soup.find_all('div', class_='x1dm5mii')
    print(soup.find_all('div'))
    
    # Extract text from spans with class _ap3a
    extracted_texts = []
    for div in div_elements:
        span = div.find('span', class_='_ap3a')
        if span:
            extracted_texts.append(span.get_text())
    
    return extracted_texts

# Replace 'username' with the actual Instagram username
username = 'louie3r'
texts = fetch_instagram_data(username)
print(texts)
# Print the extracted texts
for i, text in enumerate(texts, 1):
    print(f"Text {i}: {text}")