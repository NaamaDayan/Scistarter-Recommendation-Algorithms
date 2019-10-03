from Location_based_features import is_project_reachable_to_user, get_user_loc
from Strategy import Strategy
from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd
import scipy

class SVD(Strategy):

    def __init__(self, data_items):
        self.name = 'SVD'
        self.data_items = data_items
        matrix = scipy.sparse.csr_matrix(self.data_items.values).asfptype()
        u, sigma, self.Qt = svds(matrix, k=50)
        self.projects_predicted_ratings = None
        self.user = None

    def get_recommendations(self, user_index, k, ip_address):
        known_user_projects = self.data_items.loc[user_index]
        known_user_projects = known_user_projects[known_user_projects > 0].index
        qt_df = pd.DataFrame(self.Qt, columns=self.data_items.columns)
        projects_predicted_ratings = \
            [[i, np.dot(np.dot(self.data_items.loc[user_index], self.Qt.transpose()), qt_df[i])]
             for i in self.data_items.columns
             if i not in known_user_projects]
        projects_predicted_ratings = sorted(projects_predicted_ratings, key=lambda i: i[1], reverse=True)
        self.projects_predicted_ratings = projects_predicted_ratings
        self.user = user_index
        projects_predicted_ratings = [i[0] for i in projects_predicted_ratings]
        # projects_predicted_ratings = self.remove_unreachable_projects(projects_predicted_ratings, ip_address)
        return projects_predicted_ratings[:k]

    def remove_unreachable_projects(self, recommended_projects, ip_address):
        user_loc = get_user_loc(ip_address)
        return [project for project in recommended_projects if is_project_reachable_to_user(user_loc, project)]


    def get_highest_online_project(self):
        from Recommender import is_online_project, recommend_default_online
        online_similar_projects = list(filter(lambda x: is_online_project(x[0]), self.projects_predicted_ratings))
        if len(online_similar_projects) == 0:
            return recommend_default_online(self.user)
        return online_similar_projects[0][0]
