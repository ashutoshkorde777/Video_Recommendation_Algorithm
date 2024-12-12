from flask import Flask, request, jsonify
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import numpy as np

# Load data
viewed_posts = pd.read_csv('viewed_posts.csv')
liked_posts = pd.read_csv('liked_posts.csv')
rated_posts = pd.read_csv('rated_posts.csv')
inspired_posts = pd.read_csv('inspired_posts.csv')
users_data = pd.read_csv('cleaned_users_data.csv')
posts_summary = pd.read_csv('cleaned_summary_posts.csv')

app = Flask(__name__)

class Recommender:
    def __init__(self, posts_summary, rated_posts):
        self.posts_summary = posts_summary
        self.rated_posts = rated_posts
        
        # Initialize collaborative filtering model (SVD)
        self.svd_model = None
        self.create_svd_model()

    def create_svd_model(self):
        """Create an SVD model using ratings data for collaborative filtering"""
        ratings_matrix = self.rated_posts.pivot_table(index='User ID', columns='Post ID', values='Rating Percent', aggfunc=np.mean).fillna(0)
        svd = TruncatedSVD(n_components=20)  
        self.svd_model = svd.fit_transform(ratings_matrix)
        self.svd_matrix = pd.DataFrame(self.svd_model, index=ratings_matrix.index)

    def content_based(self, user_posts):
        """Content-based recommendation with added diversity in categories or tags"""
        if not user_posts:
            return []
        
        categories = self.posts_summary[self.posts_summary['Post ID'].isin(user_posts)]['category_name'].unique()
        
        recommended = self.posts_summary[self.posts_summary['category_name'].isin(categories)]
        return recommended['Post ID'].sample(n=10).tolist()  # Randomize output for diversity

    def collaborative(self, user_id):
        """Collaborative filtering recommendations using SVD"""
        if self.svd_model is None:
            return []
        ratings_matrix = self.rated_posts.pivot_table(index='User ID', columns='Post ID', values='Rating Percent', aggfunc=np.mean).fillna(0)
        user_idx = ratings_matrix.index.get_loc(user_id)
        user_vector = self.svd_matrix.iloc[user_idx]
        
        # Compute similarity with other users
        user_similarity = cosine_similarity([user_vector], self.svd_matrix)[0]
        similar_users = ratings_matrix.index[np.argsort(user_similarity)[::-1]][1:5]  # Top 5 similar users
        recommendations = self.rated_posts[self.rated_posts['User ID'].isin(similar_users)]['Post ID']
        
        # Decrease the weight of collaborative filtering results if too repetitive
        return recommendations.value_counts().head(5).index.tolist()

    def cold_start(self, mood):
        """Handle cold start problem with mood-based recommendations"""
        mood_map = {
            'happy': 'Motivational/Self-help',
            'sad': 'Emotional Narrative',
            'neutral': 'Philosophical Exploration'
        }
        category = mood_map.get(mood, 'Philosophical Exploration')
        
        # Check if there are posts available for the category
        category_posts = self.posts_summary[self.posts_summary['category_name'] == category]
        
        if category_posts.empty:
            print(f"No posts found for mood: {mood}")
            # Fallback to randomly selecting posts from all categories
            return self.posts_summary['Post ID'].sample(n=10).tolist()
        
        # Randomly sample posts if available
        return category_posts['Post ID'].sample(n=10).tolist()

    def hybrid_recommendations(self, user_id, user_posts, mood, category_id):
        """Generate hybrid recommendations combining content-based, collaborative, and cold-start"""
        recommendations = []

        # Content-based filtering with added diversity
        recommendations += self.content_based(user_posts)

        # Collaborative filtering
        recommendations += self.collaborative(user_id)

        # Cold-start filtering (for mood)
        if mood:
            recommendations += self.cold_start(mood)

        # Category-based filtering (if category_id is provided)
        if category_id:
            recommendations += self.posts_summary[self.posts_summary['category_id'] == int(category_id)]['Post ID'].head(10).tolist()

        # Remove duplicates and randomize the final recommendations
        return list(set(np.random.choice(recommendations, 10, replace=False)))  # Randomize final list


recommender = Recommender(posts_summary, rated_posts)



# Flask route 

@app.route('/feed', methods=['GET'])
def get_feed():
    username = request.args.get('username')
    category_id = request.args.get('category_id')
    mood = request.args.get('mood')
    
    # Retrieve and validate user ID
    user_row = users_data.loc[users_data['Username'] == username]
    if user_row.empty:
        return jsonify({'error': 'User not found'}), 404
    user_id = user_row['User ID'].squeeze()
    
   
    user_id = int(user_id)  
    
    # Combine user interactions
    user_interactions = pd.concat([ 
        viewed_posts[viewed_posts['User ID'] == user_id]['Post ID'],
        liked_posts[liked_posts['User ID'] == user_id]['Post ID'],
        rated_posts[rated_posts['User ID'] == user_id]['Post ID'],
        inspired_posts[inspired_posts['User ID'] == user_id]['Post ID']
    ]).unique().tolist()
    
    # Generate hybrid recommendations
    recommended = recommender.hybrid_recommendations(user_id, user_interactions, mood, category_id)
    
    # Get post details for recommended posts
    post_details = posts_summary[posts_summary['Post ID'].isin(recommended)][['title', 'category_name']].to_dict(orient='records')
    return jsonify(post_details)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
