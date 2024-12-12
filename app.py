from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import numpy as np

# Load data from CSV files into DataFrames
viewed_posts = pd.read_csv('viewed_posts.csv')
liked_posts = pd.read_csv('liked_posts.csv')
rated_posts = pd.read_csv('rated_posts.csv')
inspired_posts = pd.read_csv('inspired_posts.csv')
users_data = pd.read_csv('cleaned_users_data.csv')
posts_summary = pd.read_csv('cleaned_summary_posts.csv')

# Initialize Flask app
app = Flask(__name__)

class Recommender:
    """
    A recommendation system that provides content-based, collaborative, 
    and mood-based recommendations.
    """
    def __init__(self, posts_summary, rated_posts):
        self.posts_summary = posts_summary
        self.rated_posts = rated_posts

        # Initialize collaborative filtering model using SVD
        self.svd_model = None
        self.create_svd_model()

    def create_svd_model(self):
        """Create an SVD model for collaborative filtering based on user ratings."""
        # Pivot ratings data into a user-item matrix
        ratings_matrix = self.rated_posts.pivot_table(
            index='User ID', columns='Post ID', values='Rating Percent', aggfunc=np.mean
        ).fillna(0)

        # Apply Truncated SVD to reduce dimensionality
        svd = TruncatedSVD(n_components=20)
        self.svd_model = svd.fit_transform(ratings_matrix)

        # Store the transformed user feature matrix
        self.svd_matrix = pd.DataFrame(self.svd_model, index=ratings_matrix.index)

    def content_based(self, user_posts):
        """
        Generate recommendations based on the content of posts the user has interacted with.
        This method also adds diversity by recommending posts from similar categories.
        """
        if not user_posts:
            return []

        # Identify categories of the user's interacted posts
        categories = self.posts_summary[self.posts_summary['Post ID'].isin(user_posts)]['category_name'].unique()

        # Recommend posts from the same categories
        recommended = self.posts_summary[self.posts_summary['category_name'].isin(categories)]
        return recommended['Post ID'].sample(n=10).tolist()  # Randomly select posts

    def collaborative(self, user_id):
        """
        Generate recommendations using collaborative filtering with SVD.
        Recommends posts based on similar users' interactions.
        """
        if self.svd_model is None:
            return []

        # Recreate the ratings matrix
        ratings_matrix = self.rated_posts.pivot_table(
            index='User ID', columns='Post ID', values='Rating Percent', aggfunc=np.mean
        ).fillna(0)

        # Locate the user's feature vector
        user_idx = ratings_matrix.index.get_loc(user_id)
        user_vector = self.svd_matrix.iloc[user_idx]

        # Compute similarity between users
        user_similarity = cosine_similarity([user_vector], self.svd_matrix)[0]
        similar_users = ratings_matrix.index[np.argsort(user_similarity)[::-1]][1:5]  # Top 5 similar users

        # Get recommendations based on similar users' ratings
        recommendations = self.rated_posts[self.rated_posts['User ID'].isin(similar_users)]['Post ID']
        return recommendations.value_counts().head(5).index.tolist()

    def cold_start(self, mood):
        """
        Handle recommendations for new users based on their mood.
        Moods are mapped to specific categories of posts.
        """
        mood_map = {
            'happy': 'Motivational/Self-help',
            'sad': 'Emotional Narrative',
            'neutral': 'Philosophical Exploration'
        }
        category = mood_map.get(mood, 'Philosophical Exploration')

        # Get posts in the mood's corresponding category
        category_posts = self.posts_summary[self.posts_summary['category_name'] == category]

        # Fallback to random posts if no category posts are available
        if category_posts.empty:
            return self.posts_summary['Post ID'].sample(n=10).tolist()
        return category_posts['Post ID'].sample(n=10).tolist()

    def hybrid_recommendations(self, user_id, user_posts, mood, category_id):
        """
        Combine content-based, collaborative, and cold-start recommendations into a hybrid model.
        """
        recommendations = []

        # Add content-based recommendations
        recommendations += self.content_based(user_posts)

        # Add collaborative recommendations
        recommendations += self.collaborative(user_id)

        # Add cold-start recommendations if a mood is specified
        if mood:
            recommendations += self.cold_start(mood)

        # Add category-based recommendations if a category is specified
        if category_id:
            recommendations += self.posts_summary[self.posts_summary['category_id'] == int(category_id)]['Post ID'].head(10).tolist()

        # Deduplicate and randomize the final list
        return list(set(np.random.choice(recommendations, 10, replace=False)))

# Instantiate the Recommender class
recommender = Recommender(posts_summary, rated_posts)

# Flask route for home page
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

# Flask route for getting video feed recommendations
@app.route('/feed', methods=['GET'])
def get_feed():
    """
    Fetch recommendations based on user inputs:
    - username: identifies the user
    - mood: used for cold-start recommendations
    - category_id: used for category-based recommendations
    """
    username = request.args.get('username')
    category_id = request.args.get('category_id')
    mood = request.args.get('mood')

    # Retrieve user ID from username
    user_row = users_data.loc[users_data['Username'] == username]
    if user_row.empty:
        return jsonify({'error': 'User not found'}), 404
    user_id = int(user_row['User ID'].squeeze())

    # Combine all user interactions (viewed, liked, rated, inspired posts)
    user_interactions = pd.concat([
        viewed_posts[viewed_posts['User ID'] == user_id]['Post ID'],
        liked_posts[liked_posts['User ID'] == user_id]['Post ID'],
        rated_posts[rated_posts['User ID'] == user_id]['Post ID'],
        inspired_posts[inspired_posts['User ID'] == user_id]['Post ID']
    ]).unique().tolist()

    # Generate hybrid recommendations
    recommended = recommender.hybrid_recommendations(user_id, user_interactions, mood, category_id)

    # Fetch details of recommended posts
    post_details = posts_summary[posts_summary['Post ID'].isin(recommended)][['title', 'category_name']].to_dict(orient='records')
    return jsonify(post_details)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
