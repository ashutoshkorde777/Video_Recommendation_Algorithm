from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

# Load data from CSV files into pandas DataFrames
viewed_posts = pd.read_csv('viewed_posts.csv')  # Posts viewed by users
liked_posts = pd.read_csv('liked_posts.csv')  # Posts liked by users
rated_posts = pd.read_csv('rated_posts.csv')  # Posts rated by users
inspired_posts = pd.read_csv('inspired_posts.csv')  # Posts users were inspired by
users_data = pd.read_csv('cleaned_users_data.csv')  # User information
posts_summary = pd.read_csv('cleaned_summary_posts.csv')  # Summary information for posts

# Define a Recommender class to generate recommendations
class Recommender:
    def __init__(self, posts_summary, rated_posts):
        self.posts_summary = posts_summary  # Summary of posts
        self.rated_posts = rated_posts  # Ratings data for posts
        self.svd_model = None  # Placeholder for the SVD model
        self.create_svd_model()  # Create the SVD model upon initialization

    def create_svd_model(self):
        """Create an SVD model using ratings data for collaborative filtering"""
        # Create a pivot table where rows are users, columns are posts, and values are ratings
        ratings_matrix = self.rated_posts.pivot_table(
            index='User ID', columns='Post ID', values='Rating Percent', aggfunc="mean"
        ).fillna(0)  # Fill missing values with 0

        # Perform Truncated SVD on the ratings matrix for dimensionality reduction
        svd = TruncatedSVD(n_components=20)  # Reduce to 20 components
        self.svd_model = svd.fit_transform(ratings_matrix)  # Fit SVD and transform the data
        self.svd_matrix = pd.DataFrame(self.svd_model, index=ratings_matrix.index)  # Store transformed data

    def content_based(self, user_posts):
        """Content-based recommendation with added diversity in categories or tags"""
        if not user_posts:  # Return an empty list if no posts are provided
            return []

        # Identify unique categories for the user's posts
        categories = self.posts_summary[
            self.posts_summary['Post ID'].isin(user_posts)
        ]['category_name'].unique()

        # Recommend posts within the same categories
        recommended = self.posts_summary[
            self.posts_summary['category_name'].isin(categories)
        ]

        # Return a random sample of up to 10 recommended posts
        sample_size = min(10, len(recommended))  # Ensure sample size does not exceed the number of available posts
        return recommended['Post ID'].sample(n=sample_size).tolist()

    def collaborative(self, user_id):
        """Collaborative filtering recommendations using SVD"""
        if self.svd_model is None:  # Check if the SVD model exists
            return []

        # Recreate the ratings matrix
        ratings_matrix = self.rated_posts.pivot_table(
            index='User ID', columns='Post ID', values='Rating Percent', aggfunc="mean"
        ).fillna(0)

        if user_id not in ratings_matrix.index:  # If the user has no ratings, return an empty list
            return []

        # Get the index of the user in the ratings matrix
        user_idx = ratings_matrix.index.get_loc(user_id)
        user_vector = self.svd_matrix.iloc[user_idx]  # Get the user's SVD vector

        # Calculate cosine similarity between the user and all others
        user_similarity = cosine_similarity([user_vector], self.svd_matrix)[0]
        similar_users = ratings_matrix.index[
            np.argsort(user_similarity)[::-1]
        ][1:5]  # Get top 4 similar users (excluding the user)

        # Get posts rated by similar users
        recommendations = self.rated_posts[
            self.rated_posts['User ID'].isin(similar_users)
        ]['Post ID']

        # Return the top 5 most frequently recommended posts
        return recommendations.value_counts().head(5).index.tolist()

    def hybrid_recommendations(self, user_id, user_posts, mood, category_id):
        """Generate hybrid recommendations combining content-based, collaborative, and cold-start"""
        recommendations = []

        # Add content-based recommendations
        recommendations += self.content_based(user_posts)

        # Add collaborative filtering recommendations
        recommendations += self.collaborative(user_id)

        # Add mood-based recommendations if mood is provided
        if mood:
            recommendations += self.cold_start(mood)

        # Add recommendations based on category if category_id is provided
        if category_id:
            recommendations += self.posts_summary[
                self.posts_summary['category_id'] == int(category_id)
            ]['Post ID'].head(10).tolist()

        # If fewer than 10 recommendations, fill with random posts
        if len(recommendations) < 10:
            recommendations += np.random.choice(
                self.posts_summary['Post ID'], 10 - len(recommendations), replace=True
            ).tolist()

        # Return a set of 10 unique recommendations
        return list(set(np.random.choice(recommendations, 10, replace=False)))

    def cold_start(self, mood):
        """Cold-start recommendation based on mood (this is a placeholder implementation)"""
        if mood == 'happy':  # Recommend 'Happy' category posts for happy mood
            return self.posts_summary[
                self.posts_summary['category_name'] == 'Happy'
            ]['Post ID'].head(5).tolist()
        elif mood == 'sad':  # Recommend 'Sad' category posts for sad mood
            return self.posts_summary[
                self.posts_summary['category_name'] == 'Sad'
            ]['Post ID'].head(5).tolist()
        return []

    def evaluate_recommendations(self, user_id, user_interactions, recommended_posts):
        """Evaluate recommendations using MAE and RMSE"""
        # Actual user interactions
        actual_interactions = set(user_interactions)

        # Predicted interactions from recommendations
        predicted_interactions = set(recommended_posts)

        # Intersection of actual and predicted interactions
        common = actual_interactions.intersection(predicted_interactions)

        # Assign binary ratings: 1 if interacted, 0 if not
        actual_ratings = [1 if post in common else 0 for post in recommended_posts]
        predicted_ratings = [1 if post in actual_interactions else 0 for post in recommended_posts]

        # Calculate Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE)
        mae = mean_absolute_error(actual_ratings, predicted_ratings)
        rmse = np.sqrt(mean_squared_error(actual_ratings, predicted_ratings))

        return mae, rmse


# Instantiate the recommender system
recommender = Recommender(posts_summary, rated_posts)

# Evaluate recommendations for all users
all_user_ids = users_data['User ID'].unique()  # Get all unique user IDs
evaluation_results = []

for user_id in all_user_ids:
    # Gather user interactions (viewed, liked, rated, inspired posts)
    user_interactions = pd.concat([
        viewed_posts[viewed_posts['User ID'] == user_id]['Post ID'],
        liked_posts[liked_posts['User ID'] == user_id]['Post ID'],
        rated_posts[rated_posts['User ID'] == user_id]['Post ID'],
        inspired_posts[inspired_posts['User ID'] == user_id]['Post ID']
    ]).unique().tolist()

    # Generate hybrid recommendations for the user
    recommended_posts = recommender.hybrid_recommendations(
        user_id, user_interactions, mood='happy', category_id=None
    )

    # Evaluate recommendations using MAE and RMSE
    mae, rmse = recommender.evaluate_recommendations(
        user_id, user_interactions, recommended_posts
    )

    # Store evaluation results
    evaluation_results.append({
        'User ID': user_id,
        'MAE': mae,
        'RMSE': rmse
    })

# Convert evaluation results into a DataFrame for analysis
evaluation_df = pd.DataFrame(evaluation_results)

# Calculate and print average MAE and RMSE across all users
average_mae = evaluation_df['MAE'].mean()
average_rmse = evaluation_df['RMSE'].mean()
print(evaluation_df)  # Print individual user evaluation results
print(f'Average MAE for all users: {average_mae}')
print(f'Average RMSE for all users: {average_rmse}')
