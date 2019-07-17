from Strategy import Strategy
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class CFUserUser(Strategy):

    def __init__(self, data_items):
        self.data_items = data_items
        self.projects_score = None
        self.user_index = None

    def find_k_similar_users(self, user_id, metric='cosine', k=1000):
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
        return self.get_recommendations_helper(user_index, k, 200)

    def get_recommendations_helper(self, user_index, k, k_knn):
        similar_users = self.find_k_similar_users(user_index)
        if user_index in similar_users.index:
            similar_users = similar_users.drop(user_index, 0)
        similar_projects = [self.get_user_projects(user) for user in similar_users.index]
        similar_projects = list(set([item for sublist in similar_projects for item in sublist]))
        projects_scores = dict.fromkeys(similar_projects, 0)
        for s_project in similar_projects:
            for user in similar_users.index:
                projects_scores[s_project] += similar_users.loc[user] * self.data_items.loc[user][s_project]
        projects_scores = sorted(projects_scores.items(), key=lambda x: x[1], reverse=True)  # sort
        self.projects_score = projects_scores
        self.user_index = user_index
        recommended_projects = [i[0] for i in projects_scores]
        known_user_projects = self.get_user_projects(user_index)
        recommended_projects = list(filter(lambda x: x not in known_user_projects, recommended_projects))
        while len(recommended_projects) < k:
            recommended_projects = self.get_recommendations_helper(user_index, k, k_knn + 100)  # increase knn_var until sufficient variety of projects
        return recommended_projects[:k]

    def get_highest_online_project(self):
        from Recommender import is_online_project, recommend_default_online
        online_similar_projects = list(filter(lambda x: is_online_project(x[0]), self.projects_score))
        if len(online_similar_projects) == 0:
            return recommend_default_online(self.user_index)
        return online_similar_projects[0][0]
