from Location_based_features import is_project_reachable_to_user, get_user_loc
from Strategy import Strategy
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

class CFItemItem(Strategy):

    def __init__(self, data_items):
        self.name = 'CFItemItem'
        self.data_items = data_items
        self.data_matrix = self.calculate_similarity()  # project * project
        self.score = None
        self.user = None

    def calculate_similarity(self):
        data_sparse = sparse.csr_matrix(self.data_items)
        similarities = cosine_similarity(data_sparse.transpose())
        sim = pd.DataFrame(similarities, self.data_items.columns, self.data_items.columns)
        sim.columns = [int(i) for i in sim.columns]
        sim.index = [int(i) for i in sim.index]
        return sim

    def get_recommendations(self, user_index, k, ip_address):
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
        neighbourhood = self.data_matrix[similar_list].loc[similar_list]

        user_vector = self.data_items.loc[user_index].loc[similar_list]
        score = neighbourhood.dot(user_vector).div(neighbourhood.sum(1))
        for project in known_user_projects:
            if project in score.index:
                score = score.drop(project)
        # score = self.remove_unreachable_projects(score, ip_address)
        self.score = score
        self.user = user_index
        recommended_projects = score.nlargest(k).index.tolist()
        return recommended_projects


    def remove_unreachable_projects(self, projects_score, ip_address):
        user_loc = get_user_loc(ip_address)
        for project in projects_score.index:
            if not is_project_reachable_to_user(user_loc, project):
                projects_score = projects_score.drop(project)
        return projects_score

    def get_highest_online_project(self):
        from Recommender import is_online_project, recommend_default_online
        for project in self.score.index:
            if not is_online_project(project):
                self.score = self.score.drop(project)
        project = self.score.nlargest(1)
        if len(project) == 0:
            return recommend_default_online(self.user)
        return project.index[0]

