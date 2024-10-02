from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances, silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def preprocess(data):
    # 1. Select the relevant features for clustering
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']

    X = data[features]

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=4, random_state=42)
    data['cluster_kmeans'] = kmeans.fit_predict(X_scaled)
    
    return data, X_scaled

def pca(X_scaled):
    pca = PCA(n_components=2)
    # Apply PCA on the scaled feature set X_scaled and transform the data into the new 2-dimensional space.
    X_pca = pca.fit_transform(X_scaled)
    
    return X_pca