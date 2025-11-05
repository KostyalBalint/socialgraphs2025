import requests
import os
import json
import re

# Wikipedia Downloader Class, with which we download rock artists wikipedia pages in their JSON format
#this code is from our Assignment 1
class WikipediaDownloader:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def download_page_html(self, title):
        try:
            params = {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "format": "json",
                "titles": title.replace(' ', '_'),  # Use the actual title parameter
                "rvslots": "main"
            }
            print(f"Downloading: {title}")
            response = self.session.get(self.base_url, params=params)

            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error downloading {title}: {e}")
            return None

    def save_page(self, title, content):
        if content is None:
            return False

        # Create directory if it doesn't exist
        os.makedirs("wikipedia_pages", exist_ok=True)

        # Clean filename
        safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"wikipedia_pages/{safe_filename}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved: {filename}")
            return filename
        except IOError as e:
            print(f"Error saving {title}: {e}")
            return False

    def download_and_save(self, title):
        content = self.download_page_html(title)

        if content:
            return self.save_page(title, content)
        return False

downloader = WikipediaDownloader()

def download_pages(favorite_pages):
    for page_title in favorite_pages:
        print(f"\n--- Processing: {page_title} ---")

        # Download HTML version
        file_name = downloader.download_and_save(page_title)
        if(file_name):
            print(f"Successfully downloaded and saved: {file_name}")
        else:
            print(f"Failed to download or save: {page_title}")


    with open("wikipedia_pages/List of mainstream rock performers.json", "r") as f:
        html_content = f.read()

    # we had to decode the json because of the special characters
    parsed_json = json.loads(html_content)
    page_id = list(parsed_json['query']['pages'].keys())[0]
    wiki_text = parsed_json['query']['pages'][page_id]['revisions'][0]['slots']['main']['*']

    # Now extract from the properly decoded text
    pattern = r'\[\[([^\]|]+)'
    # Find the artists and saved them to the artists.txt
    matches = re.findall(pattern, wiki_text)

    # Optional: remove duplicates and sort
    artists = sorted(set(matches))

    # Save to a text file
    with open("artists.txt", "w", encoding="utf-8") as f:
        for artist in artists:
            f.write(artist + "\n")

    print(f"Extracted {len(artists)} artists and saved to artists.txt")
    with open("artists.txt", "r") as file:
        lines = file.readlines()

    with open("artists.txt", "w") as file:
        for line in lines[:-1]:
            file.write(line)
    # Open the file in read mode
    artists_file_names = []
    with open("artists.txt", "r", encoding="utf-8") as file:
        for line in file:
            artist = line.strip()  # remove leading/trailing spaces and newline
            file_name = downloader.download_and_save(artist)
            if file_name:
                artists_file_names.append(file_name)
            else:
                print(f"Failed to download or save: {page_title}")