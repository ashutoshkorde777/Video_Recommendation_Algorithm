import requests
import csv
import time
import json

# Constants for API interaction
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}
RES_ALGO = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"  

def fetch_data(endpoint, page=1, page_size=1000, resonance_algorithm=RES_ALGO):
    """
    Fetch paginated data from the specified API endpoint.

    Args:
        endpoint (str): API endpoint to fetch data from.
        page (int): Current page number for pagination.
        page_size (int): Number of items per page.
        resonance_algorithm (str): Resonance algorithm token.

    Returns:
        tuple: A tuple containing a list of items and the total number of pages.
    """
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}&resonance_algorithm={resonance_algorithm}"
    response = requests.get(url, headers=AUTH_HEADER)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  # Debugging log
        
        total_pages = data.get('max_page_size', 1)
        items = data.get('posts', [])
        return items, total_pages
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

def process_rated_posts(posts):
    """
    Process a list of rated posts to extract relevant fields.

    Args:
        posts (list): List of posts returned from the API.

    Returns:
        list: Processed list of dictionaries with extracted fields.
    """
    processed_posts = []
    for post in posts:
        processed_post = {
            'Post ID': post.get('post_id'),
            'User ID': post.get('user_id'),
            'Rating Percent': post.get('rating_percent'),
            'Rated At': post.get('rated_at')
        }
        processed_posts.append(processed_post)
    return processed_posts

def write_to_csv(filename, posts):
    """
    Write processed posts data to a CSV file.

    Args:
        filename (str): Name of the output CSV file.
        posts (list): List of processed posts to write.
    """
    if posts:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

def fetch_all_rated_posts():
    """
    Fetch all rated posts from the API using pagination.

    Returns:
        list: List of all processed rated posts.
    """
    all_rated_posts = []
    page = 1
    while True:
        posts, total_pages = fetch_data("posts/rating", page=page)
        if not posts:
            break
        
        processed_posts = process_rated_posts(posts)
        all_rated_posts.extend(processed_posts)
        
        if page >= total_pages:
            break
        
        page += 1
        time.sleep(1)  # Avoid hitting API rate limits
    
    return all_rated_posts

def main():
    """
    Main function to fetch all rated posts and save them to a CSV file.
    """
    rated_posts = fetch_all_rated_posts()
    print(f"Fetched {len(rated_posts)} rated posts")
    
    if rated_posts:
        write_to_csv('rated_posts.csv', rated_posts)

if __name__ == "__main__":
    main()
