from Location_based_features import is_project_reachable_to_user, get_user_loc
from Strategy import Strategy
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class CFUserUser(Strategy):

    def __init__(self, data_items):
        self.name = 'CFUserUser'
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

    def get_recommendations(self, user_index, known_user_projects, k, ip_address):
        return self.get_recommendations_helper(user_index, known_user_projects, k, 200, 0, ip_address)

    def get_recommendations_helper(self, user_index, known_user_projects, k, k_knn,iteration_number, ip_address):
        similar_users = self.find_k_similar_users(user_index, k=k_knn)
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
        recommended_projects = list(filter(lambda x: x not in known_user_projects, recommended_projects))
        recommended_projects = self.remove_non_active_projects(recommended_projects)
        recommended_projects = self.remove_unreachable_projects(recommended_projects, ip_address)
        if len(recommended_projects) < k and iteration_number < 10:
            recommended_projects = self.get_recommendations_helper(user_index, known_user_projects, k, k_knn + 100, iteration_number+1, ip_address)  # increase knn_var until sufficient variety of projects
        return recommended_projects[:k]

    @staticmethod
    def remove_non_active_projects(recommended_projects):
        from Recommender import non_active_projects
        return [project for project in recommended_projects if project not in non_active_projects['project'].values]

    @staticmethod
    def remove_unreachable_projects(recommended_projects, ip_address):
        user_loc = get_user_loc(ip_address)
        return [project for project in recommended_projects if is_project_reachable_to_user(user_loc, project)]

    def get_highest_online_project(self):
        from Recommender import is_online_project, recommend_default_online
        online_similar_projects = list(filter(lambda x: is_online_project(x[0]), self.projects_score))
        if len(online_similar_projects) == 0:
            return recommend_default_online(self.user_index)
        return online_similar_projects[0][0]
