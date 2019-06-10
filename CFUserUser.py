from Strategy import Strategy
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class CFUserUser(Strategy):

    def __init__(self, data_items):
        self.data_items = data_items

    def find_k_similar_users(self, user_id, metric='cosine', k=50):
        model_knn = NearestNeighbors(k, 1.0, 'brute', 30, metric)
        model_knn.fit(self.data_items)
        distances, indices = model_knn.kneighbors(
            self.data_items.iloc[user_id, :].values.reshape(1, -1), n_neighbors=k + 1)
        similarities = 1 - distances.flatten()
        return pd.Series(similarities, indices[0])

    def get_user_projects(self, user_id):
        known_user_likes = self.data_items.loc[user_id]
        known_user_likes = known_user_likes[known_user_likes > 0].index.values
        return known_user_likes

    def get_recommendations(self, user_index, k):
        similar_users = self.find_k_similar_users(user_index).drop(user_index, 0)
        similar_projects = [self.get_user_projects(user) for user in similar_users.index]
        similar_projects = list(set([item for sublist in similar_projects for item in sublist]))
        projects_scores = dict.fromkeys(similar_projects, 0)
        for s_project in similar_projects:
            for user in similar_users.index:
                projects_scores[s_project] += similar_users.loc[user] * self.data_items.loc[user][s_project]
        projects_scores = sorted(projects_scores.items(), key=lambda x: x[1], reverse=True)  # sort
        recommended_projects = [i[0] for i in projects_scores]
        known_user_projects = self.get_user_projects(user_index)
        return list(set(recommended_projects) - set(known_user_projects))[:k]
