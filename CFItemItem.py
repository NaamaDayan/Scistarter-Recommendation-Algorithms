from Strategy import Strategy
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class CFItemItem(Strategy):

    def __init__(self, data_items):
        self.data_items = data_items
        self.data_matrix = self.calculate_similarity()

    def calculate_similarity(self):
        data_sparse = sparse.csr_matrix(self.data_items)
        similarities = cosine_similarity(data_sparse.transpose())
        sim = pd.DataFrame(similarities, self.data_items.columns, self.data_items.columns)
        return sim

    def get_recommendations(self, user_index, k):
        known_user_projects = self.data_items.loc[user_index]
        known_user_projects = known_user_projects[known_user_projects > 0].index
        user_projects = self.data_matrix[known_user_projects]  # without ratings!!
        neighbourhood_size = 10
        data_neighbours = pd.DataFrame(0, user_projects.columns, range(1, neighbourhood_size + 1))
        for i in range(0, len(user_projects.columns)):
            data_neighbours.iloc[i, :neighbourhood_size] = user_projects.iloc[0:, i].sort_values(0, False)[
                                                           :neighbourhood_size].index

        # Construct the neighbourhood from the most similar items to the
        # ones our user has already liked.
        most_similar_to_likes = data_neighbours.loc[known_user_projects]
        similar_list = most_similar_to_likes.values.tolist()
        similar_list = list(set([item for sublist in similar_list for item in sublist]))
        similar_list = list(set(similar_list) - set(known_user_projects))
        neighbourhood = self.data_matrix[similar_list].loc[similar_list]

        user_vector = self.data_items.loc[user_index].loc[similar_list]

        score = neighbourhood.dot(user_vector).div(neighbourhood.sum(1))
        recommended_projects = score.nlargest(k).index.tolist()
        return recommended_projects
