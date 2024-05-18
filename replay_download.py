import requests
from bs4 import BeautifulSoup
import os

def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return response.content

def find_download_link(soup):
    return soup.find('a', class_='download-replays')

def find_next_page_link(soup):
    return soup.find('a', string='Next')

def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{extension}"
        counter += 1
    return new_filename

# Initial URL of the Spawning Tool replays page
base_url = 'https://lotv.spawningtool.com/replays/?p=&query=&after_time=&before_time=&after_played_on=&before_played_on=&coop=&patch=&order_by='
url = f'{base_url}'

while url:
    # Fetch the page content
    content = fetch_page(url)
    
    # Parse the page content
    soup = BeautifulSoup(content, 'html.parser')

    # Find the "Download these replays" link
    download_link = find_download_link(soup)

    if download_link:
        download_url = download_link['href']
        
        # Check if the download URL is absolute or relative
        if not download_url.startswith('http'):
            download_url = base_url + download_url
            
        print(f"Found download link: {download_url}")

        # Make a request to the download URL
        download_response = requests.get(download_url)
        download_response.raise_for_status()  # Ensure the request was successful

        # Define the path to save the file
        directory = os.path.join('data', 'public_replays')
        filename = 'all_replays.zip'
        unique_filename = get_unique_filename(directory, filename)
        file_path = os.path.join(directory, unique_filename)

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Save the content to a file
        with open(file_path, 'wb') as file:
            file.write(download_response.content)
        print(f"File downloaded and saved to: {file_path}")
    else:
        print("Download link not found.")
    
    # Find the "Next" link to get the next page
    next_page_link = find_next_page_link(soup)
    
    if next_page_link:
        next_url = next_page_link['href']
        
        # Check if the next URL is absolute or relative
        if not next_url.startswith('http'):
            next_url = base_url + next_url
        
        print(f"Next page URL: {next_url}")
        
        # Set the URL for the next iteration
        url = next_url
    else:
        print("No more pages.")
        url = None  # End the loop