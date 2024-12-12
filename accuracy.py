from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD


viewed_posts = pd.read_csv('viewed_posts.csv')
liked_posts = pd.read_csv('liked_posts.csv')
rated_posts = pd.read_csv('rated_posts.csv')
inspired_posts = pd.read_csv('inspired_posts.csv')
users_data = pd.read_csv('cleaned_users_data.csv')
posts_summary = pd.read_csv('cleaned_summary_posts.csv')  

class Recommender:
    def __init__(self, posts_summary, rated_posts):
        self.posts_summary = posts_summary
        self.rated_posts = rated_posts
        self.svd_model = None
        self.create_svd_model()

    def create_svd_model(self):
        """Create an SVD model using ratings data for collaborative filtering"""
        ratings_matrix = self.rated_posts.pivot_table(index='User ID', columns='Post ID', values='Rating Percent', aggfunc="mean").fillna(0)
        svd = TruncatedSVD(n_components=20)  
        self.svd_model = svd.fit_transform(ratings_matrix)
        self.svd_matrix = pd.DataFrame(self.svd_model, index=ratings_matrix.index)

    def content_based(self, user_posts):
        """Content-based recommendation with added diversity in categories or tags"""
        if not user_posts:
            return []

        categories = self.posts_summary[self.posts_summary['Post ID'].isin(user_posts)]['category_name'].unique()
        recommended = self.posts_summary[self.posts_summary['category_name'].isin(categories)]
        
        
        sample_size = min(10, len(recommended)) 
        return recommended['Post ID'].sample(n=sample_size).tolist()  

    def collaborative(self, user_id):
        """Collaborative filtering recommendations using SVD"""
        if self.svd_model is None:
            return []
        ratings_matrix = self.rated_posts.pivot_table(index='User ID', columns='Post ID', values='Rating Percent', aggfunc="mean").fillna(0)
        
        if user_id not in ratings_matrix.index:
            return []

        user_idx = ratings_matrix.index.get_loc(user_id)
        user_vector = self.svd_matrix.iloc[user_idx]
        
        
        user_similarity = cosine_similarity([user_vector], self.svd_matrix)[0]
        similar_users = ratings_matrix.index[np.argsort(user_similarity)[::-1]][1:5]  
        recommendations = self.rated_posts[self.rated_posts['User ID'].isin(similar_users)]['Post ID']
        
        return recommendations.value_counts().head(5).index.tolist()

    def hybrid_recommendations(self, user_id, user_posts, mood, category_id):
        """Generate hybrid recommendations combining content-based, collaborative, and cold-start"""
        recommendations = []
       
        recommendations += self.content_based(user_posts)

        recommendations += self.collaborative(user_id)

        
        if mood:
            recommendations += self.cold_start(mood)

        
        if category_id:
            recommendations += self.posts_summary[self.posts_summary['category_id'] == int(category_id)]['Post ID'].head(10).tolist()

        
        if len(recommendations) < 10:
            recommendations = recommendations + np.random.choice(self.posts_summary['Post ID'], 10 - len(recommendations), replace=True).tolist()

        
        return list(set(np.random.choice(recommendations, 10, replace=False)))  


    def cold_start(self, mood):
        """Cold-start recommendation based on mood (this is a placeholder implementation)"""
        
        if mood == 'happy':
            return self.posts_summary[self.posts_summary['category_name'] == 'Happy']['Post ID'].head(5).tolist()
        elif mood == 'sad':
            return self.posts_summary[self.posts_summary['category_name'] == 'Sad']['Post ID'].head(5).tolist()
        return []

    def evaluate_recommendations(self, user_id, user_interactions, recommended_posts):
        """Evaluate recommendations using MAE and RMSE"""
        
        actual_interactions = set(user_interactions)

       
        predicted_interactions = set(recommended_posts)

        
        common = actual_interactions.intersection(predicted_interactions)

        
        actual_ratings = [1 if post in common else 0 for post in recommended_posts]  # 1 for interacted, 0 for not

    
        predicted_ratings = [1 if post in actual_interactions else 0 for post in recommended_posts]

        
        mae = mean_absolute_error(actual_ratings, predicted_ratings)
        rmse = np.sqrt(mean_squared_error(actual_ratings, predicted_ratings))

        return mae, rmse



recommender = Recommender(posts_summary, rated_posts)


all_user_ids = users_data['User ID'].unique()  

evaluation_results = []


for user_id in all_user_ids:
    # Gather user interactions (viewed, liked, rated, inspired posts)
    user_interactions = pd.concat([ 
        viewed_posts[viewed_posts['User ID'] == user_id]['Post ID'], 
        liked_posts[liked_posts['User ID'] == user_id]['Post ID'], 
        rated_posts[rated_posts['User ID'] == user_id]['Post ID'], 
        inspired_posts[inspired_posts['User ID'] == user_id]['Post ID']
    ]).unique().tolist()
    
    # Generate recommendations 
    recommended_posts = recommender.hybrid_recommendations(user_id, user_interactions, mood='happy', category_id=None)
    

    mae, rmse = recommender.evaluate_recommendations(user_id, user_interactions, recommended_posts)
    
    
    evaluation_results.append({
        'User ID': user_id,
        'MAE': mae,
        'RMSE': rmse
    })


evaluation_df = pd.DataFrame(evaluation_results)


average_mae = evaluation_df['MAE'].mean()
average_rmse = evaluation_df['RMSE'].mean()

# Print results
print(evaluation_df)  
print(f'Average MAE for all users: {average_mae}')
print(f'Average RMSE for all users: {average_rmse}')
