import requests
import csv
import time
import json

# Define the API base URL and the headers with authorization token
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}
RES_ALGO = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"  

# Function to fetch data from an API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000, resonance_algorithm=RES_ALGO):
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}&resonance_algorithm={resonance_algorithm}"
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

# Function to process each rated post and extract necessary fields
def process_rated_posts(posts):
    processed_posts = []
    for post in posts:
        
        post_id = post.get('post_id')
        user_id = post.get('user_id')
        rating_percent = post.get('rating_percent')
        rated_at = post.get('rated_at')
        
        
        processed_post = {
            'Post ID': post_id,
            'User ID': user_id,
            'Rating Percent': rating_percent,
            'Rated At': rated_at
        }
        
        processed_posts.append(processed_post)
    return processed_posts

# Function to write processed rated posts to CSV
def write_to_csv(filename, posts):
    if posts:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

# Function to fetch and save all rated posts
def fetch_all_rated_posts():
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
        time.sleep(1) 
    
    return all_rated_posts

# Example usage of the function
def main():
    # Fetch all rated posts
    rated_posts = fetch_all_rated_posts()
    print(f"Fetched {len(rated_posts)} rated posts")
    
    # Save the rated posts data to a CSV file
    if rated_posts:
        write_to_csv('rated_posts.csv', rated_posts)

if __name__ == "__main__":
    main()
