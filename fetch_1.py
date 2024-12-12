import requests
import csv
import time
import json

# Define the API base URL and the headers with authorization token
BASE_URL = "https://api.socialverseapp.com"  # Base URL for the API
AUTH_HEADER = {
    "Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"
}  # Authorization token for accessing the API
RES_ALGO = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"  
# Algorithm parameter used for filtering resonance data

# Function to fetch data from an API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000, resonance_algorithm=RES_ALGO):
    """Fetch data from a specified API endpoint with pagination support."""
    # Construct the API URL with query parameters
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}&resonance_algorithm={resonance_algorithm}"
    response = requests.get(url, headers=AUTH_HEADER)  # Send GET request with authorization headers
    
    if response.status_code == 200:  # Check if the response is successful
        data = response.json()  # Parse the response JSON
        
        # Log the fetched data for debugging
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  
        
        total_pages = data.get('total_pages', 1)  # Get the total number of pages from the response
        posts = data.get('posts', [])  # Extract the 'posts' field containing the actual data
        
        return posts, total_pages
    else:  # Handle errors by logging the status code
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process each viewed post and extract necessary fields
def process_viewed_posts(posts):
    """Extract relevant information from raw posts data."""
    processed_posts = []
    for post in posts:  # Iterate through each post
        post_id = post.get('post_id')  # Extract Post ID
        user_id = post.get('user_id')  # Extract User ID
        viewed_at = post.get('viewed_at')  # Extract Viewed Timestamp
        
        # Construct a dictionary of relevant fields
        processed_post = {
            'Post ID': post_id,
            'User ID': user_id,
            'Viewed At': viewed_at
        }
        
        processed_posts.append(processed_post)  # Add processed post to the list
    return processed_posts

# Function to write processed posts to CSV
def write_to_csv(filename, posts):
    """Save processed posts data to a CSV file."""
    if posts:  # Check if there is data to save
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())  # Set CSV headers from keys
            writer.writeheader()  # Write the header row
            writer.writerows(posts)  # Write all rows of processed posts
        print(f"Data saved to {filename}")  # Log success message
    else:  # Handle case with no data
        print(f"No data to save to {filename}")

# Function to fetch and save viewed posts
def fetch_viewed_posts():
    """Fetch all viewed posts from the API and process them."""
    all_viewed_posts = []  # Initialize a list to store all processed posts
    page = 1  # Start with the first page
    while True:  # Loop through pages until all data is fetched
        posts, total_pages = fetch_data("posts/view", page=page)  # Fetch data for the current page
        if not posts:  # Break the loop if no posts are returned
            break
        processed_posts = process_viewed_posts(posts)  # Process raw posts into structured format
        all_viewed_posts.extend(processed_posts)  # Add processed posts to the main list
        
        if page >= total_pages:  # Break the loop if all pages are fetched
            break
        
        page += 1  # Increment the page counter
        time.sleep(1)  # Add delay to avoid hitting the API rate limit
    
    return all_viewed_posts

def main():
    """Main function to fetch, process, and save viewed posts data."""
    # Fetch all viewed posts
    viewed_posts = fetch_viewed_posts()
    print(f"Fetched {len(viewed_posts)} viewed posts")  # Log the total number of fetched posts
    
    # Save the viewed posts data to a CSV file
    if viewed_posts:
        write_to_csv('viewed_posts.csv', viewed_posts)

if __name__ == "__main__":
    main()  # Execute the main function
