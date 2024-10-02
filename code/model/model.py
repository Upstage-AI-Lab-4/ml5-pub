import pandas as pd
from model.preprocess import preprocess

def dfsetting():
    df = pd.read_csv('../data/spotify_songs.csv')
    return df

def recommend_songs_by_cluster_kmeans(song_name, data):
    # Search for the selected song in the dataset, ignoring case and handling missing values
    selected_song = data[data['track_name'].str.contains(song_name, case=False, na=False)]
    
    # If the song is not found, display a message and exit the function
    if selected_song.empty:
        print("Song not found.")
        return None
    
    # Retrieve the cluster to which the selected song belongs
    cluster = selected_song['cluster_kmeans'].values[0]
    
    # Find all songs that belong to the same cluster as the selected song
    recommended_songs = data[data['cluster_kmeans'] == cluster]
    
    # Exclude the selected song from the recommendations
    recommended_songs = recommended_songs[recommended_songs['track_name'] != selected_song['track_name'].values[0]]
    
    # Return only the 'track_name' and 'track_artist' columns, limited to the top 25 recommendations
    return recommended_songs[['track_name', 'track_artist']].head(30)

def model(song_name):
    data = dfsetting()
    scaled_data, scaled_x = preprocess(data)
    return_df = recommend_songs_by_cluster_kmeans(song_name, scaled_data)
    return return_df