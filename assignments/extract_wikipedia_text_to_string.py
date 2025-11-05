import re
from pathlib import Path
import json

# Extract Wikipedia text from the JSON data and remove references and digits. I used LLM to help me with cutting out the references section.
def extract_wikipedia_text(data):
    documents = []

    pages = data['query']['pages']

    for page_id, page_data in pages.items():

        # Navigate to the actual content
        if 'revisions' in page_data and len(page_data['revisions']) > 0:
            revision = page_data['revisions'][0]
            if 'slots' in revision and 'main' in revision['slots']:
                wikitext = revision['slots']['main'].get('*', '')

                if wikitext:
                    wikitext = str(wikitext)
                    ref_markers = ['==References==', '== References ==', '==references==', '== references ==']

                    cut_index = len(wikitext)  # Default to end if no references found
                    for marker in ref_markers:
                        index = wikitext.find(marker)
                        if index != -1:
                            cut_index = min(cut_index, index)

                    wikitext = wikitext[:cut_index]
                    wikitext = re.sub(r'\d+', '', wikitext)
                    documents.append(str(wikitext))

    return " ".join(documents)



# Clean the wikitext by removing templates, links, citations, HTML tags, URLs, headers, and formatting. I used LLM to help me with this function.
def clean_wikitext(text):

    # Remove {{...}} templates (like infoboxes, citations)
    text = re.sub(r'\{\{[^}]*\}\}', '', text)

    # Remove [[File:...]] and [[Image:...]]
    text = re.sub(r'\[\[(File|Image):[^\]]*\]\]', '', text)

    # Convert [[Link|Display]] to just Display
    text = re.sub(r'\[\[([^\]|]*\|)?([^\]]*)\]\]', r'\2', text)

    # Remove <ref>...</ref> citations
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)

    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove == Headers ==
    text = re.sub(r'==+[^=]*==+', '', text)

    # Remove '' and ''' (italics/bold)
    text = re.sub(r"'{2,}", '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# Main function to get cleaned Wikipedia text from a JSON file.
def get_wiki_text(current_artist_file_name):
    file_path = Path(current_artist_file_name)
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    text = extract_wikipedia_text(data)
    text = clean_wikitext(text)


    return text