import os
import pickle
import pandas as pd

def load_kmeans_model(kmeans_model_path: str):
    """Load the KMeans model from a pickle file."""
    with open(kmeans_model_path, 'rb') as file:
        kmeans_model = pickle.load(file)
    return kmeans_model

def load_data(train_data_path: str, backup_data_path: str):
    """Load the training data from a CSV file, with a backup path."""
    if os.path.exists(train_data_path):
        data = pd.read_csv(train_data_path)
    else:
        print(f"{train_data_path} not found. Loading from {backup_data_path}")
        data = pd.read_csv(backup_data_path)
    return data