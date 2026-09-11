"""
Movie Recommendation Engine
Module 12: Machine Learning - Recommendation System
Covers: Collaborative filtering, content-based filtering, hybrid approach
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationSystem:
    """
    Hybrid recommendation system combining:
    - Collaborative filtering (user-user similarity)
    - Content-based filtering (movie features)
    - Hybrid approach (combining both)
    """
    
    def __init__(self, alpha: float = 0.6):
        """
        Initialize recommendation system
        
        Args:
            alpha: Weight for collaborative filtering (0-1)
                  1-alpha is weight for content-based filtering
        """
        self.alpha = alpha
        self.user_item_matrix = None
        self.user_similarity = None
        self.content_similarity = None
        self.movie_features = None
        self.user_profiles = None
        self.movies_df = None
        self.ratings_df = None
        
    def train(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        """
        Train the recommendation system
        
        Args:
            ratings_df: DataFrame with columns [user_id, movie_id, rating, timestamp]
            movies_df: DataFrame with columns [movie_id, title, genre, director, description]
        """
        logger.info("Training recommendation system...")
        
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        
        # Step 1: Build user-item matrix
        logger.info("Building user-item matrix...")
        self.user_item_matrix = ratings_df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        # Step 2: Calculate user-user similarity (collaborative filtering)
        logger.info("Calculating user-user similarity...")
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        # Step 3: Calculate content-based similarity
        logger.info("Calculating content-based similarity...")
        self._calculate_content_similarity()
        
        # Step 4: Build user profiles
        logger.info("Building user profiles...")
        self._build_user_profiles()
        
        logger.info("Training complete!")
        
    def _calculate_content_similarity(self):
        """Calculate movie similarity based on content features"""
        # Combine movie features
        movies_df = self.movies_df.copy()
        
        # Create feature string from genre, director, and description
        movies_df['features'] = (
            movies_df['genre'].fillna('') + ' ' +
            movies_df['director'].fillna('') + ' ' +
            movies_df['description'].fillna('')
        )
        
        # Use TF-IDF for text similarity
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        feature_vectors = vectorizer.fit_transform(movies_df['features'])
        
        # Calculate similarity matrix
        self.content_similarity = cosine_similarity(feature_vectors)
        self.content_similarity = pd.DataFrame(
            self.content_similarity,
            index=movies_df['movie_id'],
            columns=movies_df['movie_id']
        )
        
        self.movie_features = feature_vectors
        
    def _build_user_profiles(self):
        """Build user preference profiles"""
        self.user_profiles = {}
        
        for user_id in self.user_item_matrix.index:
            # Get movies rated by user
            rated_movies = self.user_item_matrix.loc[user_id]
            rated_movies = rated_movies[rated_movies > 0]
            
            # Create profile: weighted average of movie features
            if len(rated_movies) > 0:
                movie_indices = [self.movies_df[self.movies_df['movie_id'] == mid].index[0] 
                               for mid in rated_movies.index 
                               if mid in self.movies_df['movie_id'].values]
                
                if movie_indices:
                    weights = rated_movies.values[:len(movie_indices)]
                    self.user_profiles[user_id] = {
                        'rated_movies': list(rated_movies.index),
                        'ratings': list(rated_movies.values),
                        'avg_rating': rated_movies.mean()
                    }
    
    def collaborative_filtering(self, user_id: int, n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """
        Get recommendations using collaborative filtering
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if user_id not in self.user_similarity.index:
            logger.warning(f"User {user_id} not in training data")
            return []
        
        # Get similar users
        similar_users = self.user_similarity[user_id].sort_values(ascending=False)[1:11]
        
        # Get movies rated by similar users
        recommendations = {}
        for similar_user, similarity_score in similar_users.items():
            rated_by_similar = self.user_item_matrix.loc[similar_user]
            rated_by_current = self.user_item_matrix.loc[user_id]
            
            # Movies rated by similar user but not by current user
            new_movies = rated_by_similar[
                (rated_by_similar > 0) & 
                (rated_by_current == 0)
            ]
            
            for movie_id, rating in new_movies.items():
                if movie_id not in recommendations:
                    recommendations[movie_id] = []
                recommendations[movie_id].append(rating * similarity_score)
        
        # Aggregate scores
        final_scores = {
            movie_id: np.mean(scores)
            for movie_id, scores in recommendations.items()
        }
        
        # Return top N
        sorted_recs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:n_recommendations]
    
    def content_based(self, user_id: int, n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """
        Get recommendations using content-based filtering
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if user_id not in self.user_item_matrix.index:
            logger.warning(f"User {user_id} not in training data")
            return []
        
        # Get movies rated by user
        rated_movies = self.user_item_matrix.loc[user_id]
        rated_movies = rated_movies[rated_movies > 0].index.tolist()
        
        if not rated_movies:
            return []
        
        # Calculate similarity to rated movies
        recommendations = {}
        
        for movie_id in self.content_similarity.index:
            if movie_id not in rated_movies:
                # Average similarity to all rated movies
                similarities = [
                    self.content_similarity.loc[movie_id, rated_movie]
                    for rated_movie in rated_movies
                    if rated_movie in self.content_similarity.index
                ]
                
                if similarities:
                    avg_similarity = np.mean(similarities)
                    recommendations[movie_id] = avg_similarity
        
        # Return top N
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:n_recommendations]
    
    def hybrid_recommend(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Get recommendations using hybrid approach
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of recommendation dictionaries
        """
        # Get collaborative recommendations
        collab_recs = dict(self.collaborative_filtering(user_id, n_recommendations * 2))
        
        # Get content-based recommendations
        content_recs = dict(self.content_based(user_id, n_recommendations * 2))
        
        # Normalize scores to 0-1
        if collab_recs:
            max_collab = max(collab_recs.values())
            collab_recs = {k: v / max_collab for k, v in collab_recs.items()}
        
        if content_recs:
            max_content = max(content_recs.values())
            content_recs = {k: v / max_content for k, v in content_recs.items()}
        
        # Combine scores
        hybrid_scores = {}
        all_movies = set(collab_recs.keys()) | set(content_recs.keys())
        
        for movie_id in all_movies:
            collab_score = collab_recs.get(movie_id, 0) * self.alpha
            content_score = content_recs.get(movie_id, 0) * (1 - self.alpha)
            hybrid_scores[movie_id] = collab_score + content_score
        
        # Get top recommendations with movie details
        sorted_scores = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for movie_id, score in sorted_scores[:n_recommendations]:
            movie_info = self.movies_df[self.movies_df['movie_id'] == movie_id].iloc[0]
            recommendations.append({
                'movie_id': movie_id,
                'title': movie_info['title'],
                'genre': movie_info['genre'],
                'predicted_rating': float(score),
                'confidence': float(score)
            })
        
        return recommendations
    
    def evaluate(self, test_ratings_df: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate recommendation system on test data
        
        Args:
            test_ratings_df: DataFrame with test ratings
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating recommendation system...")
        
        # Calculate RMSE, MAE, precision@K
        predictions = []
        actuals = []
        
        for _, row in test_ratings_df.iterrows():
            user_id, movie_id, actual_rating = row['user_id'], row['movie_id'], row['rating']
            
            recs = self.hybrid_recommend(user_id, n_recommendations=100)
            rec_dict = {r['movie_id']: r['predicted_rating'] for r in recs}
            
            predicted_rating = rec_dict.get(movie_id, 2.5)  # Default to neutral rating
            predictions.append(predicted_rating)
            actuals.append(actual_rating)
        
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mae = np.mean(np.abs(predictions - actuals))
        
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'mean_actual_rating': float(np.mean(actuals)),
            'mean_predicted_rating': float(np.mean(predictions))
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def save(self, filepath: str):
        """Save model to file"""
        joblib.dump(self, filepath)
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from file"""
        model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
        return model


# Example usage and training
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    
    # Generate synthetic ratings
    n_users, n_movies = 100, 50
    user_ids = np.repeat(np.arange(1, n_users + 1), 10)
    movie_ids = np.tile(np.arange(1, 11), n_users)
    ratings = np.random.randint(1, 6, len(user_ids))
    
    ratings_df = pd.DataFrame({
        'user_id': user_ids,
        'movie_id': movie_ids,
        'rating': ratings,
        'timestamp': pd.date_range('2024-01-01', periods=len(user_ids), freq='H')
    })
    
    # Generate synthetic movies
    genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi']
    directors = ['Director A', 'Director B', 'Director C', 'Director D']
    
    movies_df = pd.DataFrame({
        'movie_id': range(1, n_movies + 1),
        'title': [f'Movie {i}' for i in range(1, n_movies + 1)],
        'genre': np.random.choice(genres, n_movies),
        'director': np.random.choice(directors, n_movies),
        'description': [f'Description for movie {i}' for i in range(1, n_movies + 1)]
    })
    
    # Train model
    rec_system = RecommendationSystem(alpha=0.6)
    rec_system.train(ratings_df, movies_df)
    
    # Get recommendations for user 1
    recommendations = rec_system.hybrid_recommend(user_id=1, n_recommendations=5)
    print("Recommendations for User 1:")
    for rec in recommendations:
        print(f"  - {rec['title']} ({rec['genre']}) - Confidence: {rec['confidence']:.2f}")
    
    # Evaluate model
    test_df = ratings_df.sample(frac=0.2, random_state=42)
    metrics = rec_system.evaluate(test_df)
    print(f"\nEvaluation Metrics: {metrics}")
    
    # Save model
    rec_system.save('/mnt/user-data/outputs/recommendation_model.pkl')
