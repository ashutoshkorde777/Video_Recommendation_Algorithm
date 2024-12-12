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
        
        
        total_pages = data.get('total_pages', 1)  
        posts = data.get('posts', [])  
        
        return posts, total_pages
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process each viewed post and extract necessary fields
def process_viewed_posts(posts):
    processed_posts = []
    for post in posts:
        
        post_id = post.get('post_id')
        user_id = post.get('user_id')
        viewed_at = post.get('viewed_at')
        
        
        processed_post = {
            'Post ID': post_id,
            'User ID': user_id,
            'Viewed At': viewed_at
        }
        
        processed_posts.append(processed_post)
    return processed_posts

# Function to write processed posts to CSV
def write_to_csv(filename, posts):
    if posts:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

# Function to fetch and save viewed posts
def fetch_viewed_posts():
    all_viewed_posts = []
    page = 1
    while True:
        posts, total_pages = fetch_data("posts/view", page=page)  
        if not posts:
            break
        processed_posts = process_viewed_posts(posts)  
        all_viewed_posts.extend(processed_posts)
        
       
        if page >= total_pages:
            break
        
        page += 1
        time.sleep(1)
    
    return all_viewed_posts


def main():
    # Fetch all viewed posts
    viewed_posts = fetch_viewed_posts()
    print(f"Fetched {len(viewed_posts)} viewed posts")
    
    # Save the viewed posts data to a CSV file
    if viewed_posts:
        write_to_csv('viewed_posts.csv', viewed_posts)

if __name__ == "__main__":
    main()
