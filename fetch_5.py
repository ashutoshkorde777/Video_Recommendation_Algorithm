import requests
import csv
import time
import json

# Define the API base URL and the headers with authorization token
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}

# Flatten nested dictionary into a single-level dictionary
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v)))  
        else:
            items.append((new_key, v))
    return dict(items)

# Function to fetch data from an API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000):
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}"
    response = requests.get(url, headers=AUTH_HEADER)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  
        
        total_pages = data.get('max_page_size', 1)
        items = data.get('posts', [])
        return items, total_pages
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process each post and flatten its fields
def process_summary_posts(posts):
    processed_posts = []
    for post in posts:
        processed_posts.append(flatten_dict(post))  
    return processed_posts

# Function to write processed summary posts to CSV
def write_to_csv(filename, posts):
    if posts:
        
        header = set()
        for post in posts:
            header.update(post.keys())
        header = sorted(header)
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(posts)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

# Function to fetch and save all summary posts
def fetch_all_summary_posts():
    all_summary_posts = []
    page = 1
    while True:
        posts, total_pages = fetch_data("posts/summary/get", page=page)
        if not posts:
            break
        processed_posts = process_summary_posts(posts)  
        all_summary_posts.extend(processed_posts)
        
        if page >= total_pages:
            break
        page += 1
        time.sleep(1)  
    
    return all_summary_posts

# Example usage of the function
def main():
    # Fetch all summary posts
    summary_posts = fetch_all_summary_posts()
    print(f"Fetched {len(summary_posts)} summary posts")
    
    # Save the summary posts data to a CSV file
    if summary_posts:
        write_to_csv('summary_posts.csv', summary_posts)

if __name__ == "__main__":
    main()
