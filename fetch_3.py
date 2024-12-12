import requests
import csv
import time
import json

# Define the API base URL and the headers with the authorization token
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}
RES_ALGO = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"  # Resonance algorithm identifier

# Function to fetch data from an API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000, resonance_algorithm=RES_ALGO):
    """
    Fetch data from the specified API endpoint using pagination.

    Args:
        endpoint (str): The API endpoint to fetch data from.
        page (int): The current page number to fetch.
        page_size (int): The number of items per page.
        resonance_algorithm (str): The algorithm parameter for filtering data.

    Returns:
        tuple: A list of items and the total number of pages.
    """
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}&resonance_algorithm={resonance_algorithm}"
    response = requests.get(url, headers=AUTH_HEADER)

    if response.status_code == 200:
        data = response.json()

        # Log fetched data for debugging
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))

        total_pages = data.get('max_page_size', 1)  # Total number of pages
        items = data.get('posts', [])  # Extract posts from the response

        return items, total_pages
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process each inspired post and extract necessary fields
def process_inspired_posts(posts):
    """
    Process raw inspired posts data to extract required fields.

    Args:
        posts (list): List of raw posts data.

    Returns:
        list: List of processed posts with selected fields.
    """
    processed_posts = []
    for post in posts:
        # Extract required fields
        post_id = post.get('post_id')
        user_id = post.get('user_id')
        inspired_at = post.get('inspired_at')

        # Create a processed post dictionary
        processed_post = {
            'Post ID': post_id,
            'User ID': user_id,
            'Inspired At': inspired_at
        }

        processed_posts.append(processed_post)
    return processed_posts

# Function to write processed posts to a CSV file
def write_to_csv(filename, posts):
    """
    Write processed posts data to a CSV file.

    Args:
        filename (str): Name of the CSV file to save data.
        posts (list): List of processed posts.
    """
    if posts:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            # Write data to CSV
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

# Function to fetch and save all inspired posts
def fetch_all_inspired_posts():
    """
    Fetch all inspired posts across all pages and process them.

    Returns:
        list: List of all processed inspired posts.
    """
    all_inspired_posts = []
    page = 1
    while True:
        # Fetch data from the "posts/inspire" endpoint
        posts, total_pages = fetch_data("posts/inspire", page=page)
        if not posts:
            break

        # Process and store posts
        processed_posts = process_inspired_posts(posts)
        all_inspired_posts.extend(processed_posts)

        # Check if we have reached the last page
        if page >= total_pages:
            break

        page += 1  # Move to the next page
        time.sleep(1)  # Avoid hitting API rate limits

    return all_inspired_posts

# Main function to coordinate the data fetching and saving
def main():
    """Main function to fetch and save inspired posts."""
    inspired_posts = fetch_all_inspired_posts()
    print(f"Fetched {len(inspired_posts)} inspired posts")

    # Save the inspired posts data to a CSV file
    if inspired_posts:
        write_to_csv('inspired_posts.csv', inspired_posts)

if __name__ == "__main__":
    main()
