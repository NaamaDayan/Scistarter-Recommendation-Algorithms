from Strategy import Strategy
from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd
import scipy

class SVD(Strategy):

    def __init__(self, data_items):
        self.data_items = data_items
        matrix = scipy.sparse.csr_matrix(self.data_items.values).asfptype()
        u, sigma, self.Qt = svds(matrix, k=50)

    def get_recommendations(self, user_index, k):
        known_user_projects = self.data_items.loc[user_index]
        known_user_projects = known_user_projects[known_user_projects > 0].index
        qt_df = pd.DataFrame(self.Qt, columns=self.data_items.columns)
        projects_predicted_ratings = \
            [[i, np.dot(np.dot(self.data_items.loc[user_index], self.Qt.transpose()), qt_df[i])]
             for i in self.data_items.columns
             if i not in known_user_projects]
        projects_predicted_ratings = sorted(projects_predicted_ratings, key=lambda i: i[1])
        projects_predicted_ratings = [i[0] for i in projects_predicted_ratings]
        return projects_predicted_ratings[-k:]
