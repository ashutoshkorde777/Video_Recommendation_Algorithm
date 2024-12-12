import requests
import csv
import time
import json

# Define the API base URL and headers with the authorization token
BASE_URL = "https://api.socialverseapp.com"  # Base URL for the API
AUTH_HEADER = {"Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"}  # Authentication token header

# Function to fetch data from the API endpoint with pagination
def fetch_data(endpoint, page=1, page_size=1000):
    # Construct the full API URL with pagination parameters
    url = f"{BASE_URL}/{endpoint}?page={page}&page_size={page_size}"
    # Send a GET request to the API
    response = requests.get(url, headers=AUTH_HEADER)
    
    if response.status_code == 200:  # Check if the request was successful
        data = response.json()  # Parse the JSON response
        
        # Print fetched data for debugging
        print(f"Fetched data from {endpoint} (Page {page}):")
        print(json.dumps(data, indent=4))  
        
        # Extract the total number of pages and user data from the response
        total_pages = data.get('max_page_size', 1)  # Default to 1 if not provided
        users = data.get('users', [])  # Default to an empty list if no users found
        
        return users, total_pages  # Return the list of users and total pages
    else:
        # Print an error message if the request fails
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return [], 0  # Return an empty list and 0 pages in case of failure

# Function to process user data and extract necessary fields
def process_users(users):
    processed_users = []  # List to hold processed user data
    for user in users:
        # Extract and map required fields from the user data
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
        processed_users.append(processed_user)  # Add the processed user to the list
    return processed_users

# Function to write processed user data to a CSV file
def write_to_csv(filename, data):
    if data:  # Check if there is data to write
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            # Create a CSV writer using the keys from the first data entry as headers
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()  # Write the header row
            writer.writerows(data)  # Write all data rows
        print(f"Data saved to {filename}")  # Confirm data has been saved
    else:
        print(f"No data to save to {filename}")  # Notify if no data is available

# Function to fetch and save all user data
def fetch_all_users():
    all_users = []  # List to hold all user data
    page = 1  # Start with the first page
    while True:
        # Fetch users from the current page
        users, total_pages = fetch_data("users/get_all", page=page)  
        if not users:  # Exit loop if no users are found
            break
        processed_users = process_users(users)  # Process the user data
        all_users.extend(processed_users)  # Add processed users to the main list
        
        # Check if the current page is the last page
        if page >= total_pages:
            break
        
        page += 1  # Move to the next page
        time.sleep(1)  # Pause for 1 second to avoid overloading the API
    
    return all_users  # Return the complete list of users

# Example usage of the function
def main():
    # Fetch all users
    users = fetch_all_users()
    print(f"Fetched {len(users)} users")  # Print the number of users fetched
    
    # Save the user data to a CSV file
    if users:
        write_to_csv('users_data.csv', users)  # Save data to 'users_data.csv'

# Run the script
if __name__ == "__main__":
    main()
