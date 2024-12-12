import requests
import csv
import time
import json

# Define the API base URL and the headers with the authorization token
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}

# Function to flatten a nested dictionary into a single-level dictionary
# This is useful for converting complex JSON data into a flat structure for CSV export
def flatten_dict(d, parent_key='', sep='_'):
    items = []  # List to hold flattened key-value pairs
    for k, v in d.items():
        # Create a new key by appending the parent key and current key
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):  # If the value is a dictionary, recursively flatten it
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):  # If the value is a list, convert it to JSON string
            items.append((new_key, json.dumps(v)))
        else:  # Otherwise, just append the key-value pair
            items.append((new_key, v))
    return dict(items)

# Function to fetch data from the API with pagination
# This ensures we can handle APIs that return large datasets in chunks
def fetch_data(endpoint, page=1, page_size=1000):
    # Construct the API URL with pagination parameters
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}"
    # Send a GET request to the API
    response = requests.get(url, headers=AUTH_HEADER)
    
    if response.status_code == 200:  # If the response is successful
        data = response.json()  # Parse the JSON response
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  # Pretty-print the fetched data
        
        # Extract the total number of pages and the actual items
        total_pages = data.get('max_page_size', 1)
        items = data.get('posts', [])
        return items, total_pages
    else:  # If the request failed, print an error message
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process a list of posts by flattening their fields
def process_summary_posts(posts):
    processed_posts = []  # List to hold processed posts
    for post in posts:
        processed_posts.append(flatten_dict(post))  # Flatten each post and append to the list
    return processed_posts

# Function to write the processed posts to a CSV file
def write_to_csv(filename, posts):
    if posts:  # Check if there are posts to write
        # Dynamically generate the header from all keys in the posts
        header = set()
        for post in posts:
            header.update(post.keys())
        header = sorted(header)  # Sort the header alphabetically
        
        # Open the CSV file for writing
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)  # Create a CSV writer with the header
            writer.writeheader()  # Write the header row
            writer.writerows(posts)  # Write all rows of posts
        print(f"Data saved to {filename}")
    else:  # If no posts are available to write, print a message
        print(f"No data to save to {filename}")

# Function to fetch and process all summary posts across all pages
def fetch_all_summary_posts():
    all_summary_posts = []  # List to hold all posts from all pages
    page = 1  # Start with the first page
    while True:
        # Fetch posts for the current page
        posts, total_pages = fetch_data("posts/summary/get", page=page)
        if not posts:  # If no posts are returned, stop the loop
            break
        processed_posts = process_summary_posts(posts)  # Process the fetched posts
        all_summary_posts.extend(processed_posts)  # Add processed posts to the main list
        
        if page >= total_pages:  # If the last page is reached, stop the loop
            break
        page += 1  # Increment the page number
        time.sleep(1)  # Pause for 1 second to respect API rate limits
    
    return all_summary_posts

# Main function to execute the workflow
def main():
    # Fetch all summary posts from the API
    summary_posts = fetch_all_summary_posts()
    print(f"Fetched {len(summary_posts)} summary posts")
    
    # Save the fetched and processed posts to a CSV file
    if summary_posts:
        write_to_csv('summary_posts.csv', summary_posts)

# Entry point of the script
if __name__ == "__main__":
    main()
