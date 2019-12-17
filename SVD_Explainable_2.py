from CFItemItem import CFItemItem
from Location_based_features import is_project_reachable_to_user, get_user_loc
from MF import MF
from Strategy import Strategy
from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd
import scipy
from CFUserUser import *
from funk_svd import SVD

class SVD_Explainable_2(Strategy):

    def __init__(self, data_items, ratings_train, ratings_validation):
        self.name = 'SVD_Explainable_2'
        self.data_items = data_items
        self.ratings_train = ratings_train
        self.ratings_validation = ratings_validation
        self.explanations_matrix = pd.read_csv('explanation_matrix_user_based.csv')
        self.svd = SVD(self.explanations_matrix, learning_rate=0.005, regularization=0.005, n_epochs=1000, n_factors=15, min_rating=1, max_rating=2, lambda_=0.000)
        self.svd.fit(X=ratings_train,X_val=ratings_validation, early_stopping=True, shuffle=False)
        # self.predicted_matrix = pd.DataFrame(self.mf.full_matrix(), index=data_items.index, columns=data_items.columns)

    def get_users_of_project(self,project):
        users_of_project = self.data_items[project]
        users_of_project = users_of_project[users_of_project > 0].index.values
        return users_of_project

    def get_user_projects(self, user_id):
        known_user_likes = self.data_items.loc[user_id]
        known_user_likes = known_user_likes[known_user_likes > 0].index.values
        return known_user_likes

    def calc_explanation_score_user_based(self,user_id,project,cf_user_user):
        k=50
        similar_users = cf_user_user.find_k_similar_users(user_id, k=k).index
        user_liked_project = self.get_users_of_project(project)
        return len(np.intersect1d(similar_users, user_liked_project))/len(similar_users)

    def calc_explanation_score_item_based(self,user_id,project,cf_item_item):
        k=10
        similar_projects = cf_item_item.get_k_similar_projects(project, k=k)
        known_user_projects = self.get_user_projects(user_id)
        return len(np.intersect1d(similar_projects, known_user_projects))/len(similar_projects)

    def get_explanations_matrix(self):
        i=0
        #cf_item_item = CFItemItem(self.data_items)
        cf_user_user = CFUserUser(self.data_items)
        explanation_matrix = pd.DataFrame(0, columns=self.data_items.columns, index=self.data_items.index)
        print (explanation_matrix.shape)
        for user_id in explanation_matrix.index:
            print (i)
            i += 1
            for project in explanation_matrix.columns:
                explanation_matrix.loc[user_id][project] = self.calc_explanation_score_user_based(user_id, project,cf_user_user)
        return explanation_matrix

    def get_recommendations(self, user_index, known_user_projects, k, ip_address):
        projects_predicted_ratings = \
            [[project, self.svd.predict_pair(user_index, project, clip=False)]
             for project in self.data_items.columns
             if project not in known_user_projects]

        # projects_predicted_ratings = \
        #     [[project, self.predicted_matrix.loc[user_index][project]]
        #      for project in self.data_items.columns
        #      if project not in known_user_projects]
        projects_predicted_ratings = sorted(projects_predicted_ratings, key=lambda i: i[1], reverse=True)
        self.projects_predicted_ratings = projects_predicted_ratings
        self.user = user_index
        projects_predicted_ratings = [i[0] for i in projects_predicted_ratings]
        projects_predicted_ratings = self.remove_non_active_projects(projects_predicted_ratings)
        # projects_predicted_ratings = self.remove_unreachable_projects(projects_predicted_ratings, ip_address)
        return projects_predicted_ratings[:k]

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
        online_similar_projects = list(filter(lambda x: is_online_project(x[0]), self.projects_predicted_ratings))
        if len(online_similar_projects) == 0:
            return recommend_default_online(self.user)
        return online_similar_projects[0][0]
