import requests
import csv
import time
import json

# Define the API base URL and headers with the authorization token
BASE_URL = "https://api.socialverseapp.com"
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}

# Function to fetch data from the API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000):
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}"
    response = requests.get(url, headers=AUTH_HEADER)
    
    if response.status_code == 200:
        data = response.json()
        
        
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  
        
        
        total_pages = data.get('max_page_size', 1)  
        users = data.get('users', [])  
        
        return users, total_pages
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0

# Function to process user data and extract necessary fields
def process_users(users):
    processed_users = []
    for user in users:
        
        processed_user = {
            'User ID': user.get('id'),
            'First Name': user.get('first_name'),
            'Last Name': user.get('last_name'),
            'Username': user.get('username'),
            'Email': user.get('email'),
            'Role': user.get('role'),
            'Profile URL': user.get('profile_url'),
            'Bio': user.get('bio'),
            'Website URL': user.get('website_url'),
            'Instagram URL': user.get('instagram-url'),
            'YouTube URL': user.get('youtube_url'),
            'TikTok URL': user.get('tictok_url'),
            'Is Verified': user.get('isVerified'),
            'Referral Code': user.get('referral_code'),
            'Has Wallet': user.get('has_wallet'),
            'Last Login': user.get('last_login'),
            'Share Count': user.get('share_count'),
            'Post Count': user.get('post_count'),
            'Following Count': user.get('following_count'),
            'Follower Count': user.get('follower_count'),
            'Is Online': user.get('is_online'),
            'Latitude': user.get('latitude'),
            'Longitude': user.get('longitude'),
        }
        processed_users.append(processed_user)
    return processed_users

# Function to write processed user data to CSV
def write_to_csv(filename, data):
    if data:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filename}")
    else:
        print(f"No data to save to {filename}")

# Function to fetch and save all user data
def fetch_all_users():
    all_users = []
    page = 1
    while True:
        users, total_pages = fetch_data("users/get_all", page=page)  
        if not users:
            break
        processed_users = process_users(users)  
        all_users.extend(processed_users)
        
        
        if page >= total_pages:
            break
        
        page += 1
        time.sleep(1)  
    
    return all_users

# Example usage of the function
def main():
    # Fetch all users
    users = fetch_all_users()
    print(f"Fetched {len(users)} users")
    
    # Save the user data to a CSV file
    if users:
        write_to_csv('users_data.csv', users)

if __name__ == "__main__":
    main()
