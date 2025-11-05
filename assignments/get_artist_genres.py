# Cell 1 - Markdown
# Extract Genres from Wikipedia JSON Files

# Cell 2 - Code
import json
import re
from pathlib import Path

#This is the AI generated code which was asked in Week7 assigment. For this we used Claude. We also tested it with multiple json files to check if it is working properly.
# Cell 3 - Code
def extract_genres_from_infobox(text):
    """
    Extract genres from Wikipedia infobox format.
    Looks for patterns like: | genre = {{flatlist| or {{hlist|

    Args:
        text: The Wikipedia page text content

    Returns:
        List of genres found
    """
    genres = []

    # Pattern to match genre line in infobox
    # Looks for "| genre" followed by "=" and captures content until next parameter
    genre_pattern = r'\|\s*genre\s*=\s*(.+?)(?=\n\|[a-z_]|\n\}\})'

    match = re.search(genre_pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        genre_text = match.group(1)

        # Extract text within [[ ]] brackets (wiki links)
        wiki_links = re.findall(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]', genre_text)

        # Clean up the genres
        genres = [genre.strip() for genre in wiki_links if genre.strip()]

    return genres

# Cell 4 - Code
def process_json_file(filepath):
    """
    Process a single JSON file and extract genres from Wikipedia API format.

    Args:
        filepath: Path to the JSON file

    Returns:
        Dictionary with artist name and genres
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Navigate the Wikipedia API JSON structure
        text = ""
        artist_name = ""

        # Wikipedia API format: query.pages.[page_id].revisions[0].slots.main.*
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            # Get the first (and usually only) page
            page_id = list(pages.keys())[0]
            page_data = pages[page_id]

            # Get title
            artist_name = page_data.get('title', '')

            # Get content from revisions
            if 'revisions' in page_data and len(page_data['revisions']) > 0:
                revision = page_data['revisions'][0]
                if 'slots' in revision and 'main' in revision['slots']:
                    text = revision['slots']['main'].get('*', '')

        # Fallback: try other possible structures
        if not text:
            for key in ['*', 'content', 'text', 'wikitext']:
                if key in data:
                    text = data[key]
                    break

        # If still no artist name, use filename
        if not artist_name:
            artist_name = Path(filepath).stem

        genres = extract_genres_from_infobox(text)

        return {
            'artist': artist_name,
            'genres': genres
        }

    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return None

# Cell 5 - Code
def process_all_json_files(directory):
    """
    Process all JSON files in a directory.

    Args:
        directory: Path to directory containing JSON files

    Returns:
        List of dictionaries with artist names and their genres
    """
    results = []

    # Get all JSON files in directory
    json_files = list(Path(directory).glob('*.json'))

    print(f"Found {len(json_files)} JSON files")

    for filepath in json_files:
        result = process_json_file(filepath)
        if result:
            results.append(result)
            print(f"Processed: {result['artist']} - {len(result['genres'])} genres found")

    return results

