from CFItemItem import CFItemItem
from CFUserUser import CFUserUser
from Location_based_features import is_project_reachable_to_user, get_user_loc
from Strategy import Strategy
import pandas as pd
from collections import Counter
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from SVD import SVD

class ContentBased(Strategy):



    def __init__(self, data_items, hybrid_alg):
        self.name = 'ContentBased2'
        self.data_items = data_items
        self.projects_content = pd.read_csv('content_similarity.csv').set_index('project_id')
        self.data_matrix = self.calculate_similarity()  # project * project
        self.hybrid_alg = hybrid_alg
        self.score = None
        self.user = None

    @staticmethod
    def one_hot_vector(value, mapping):
        arr = [0] * len(mapping)
        index = mapping[value] if value in mapping.keys() else -1
        if index != -1:
            arr[mapping[value]] = 1
        return arr

    def calculate_similarity(self):
        topic2_mapping = {'Cell & Molecular': 0, 'Chemistry': 1, 'Ecology & Environment': 2, 'Pollution': 3,
                          'Geography': 4, 'Geology & Earth Science': 5, 'Anthropology': 6, 'Food & Agriculture': 7,
                          'Pets': 8, 'Psychology': 9, 'Transportation & Infrastructure': 10, 'Astronomy & Space': 11,
                          'Chemistry': 12, 'Computers & Technology': 13, 'Math & Physics': 14, 'Health & Medicine': 15,
                          'Tools': 16, 'Platform': 17, 'NotCitSci': 18, 'Unknown': 19}
        topic1_mapping = {'Earth & Life Sciences': 0, 'Behavior & Social Sciences': 1,
                          'Engineering & Physical Sciences': 2, 'Health & Medicine': 3, 'Other': 4}
        time_per_participation_mapping = {250: 0, 251: 0, 252: 0, 209: 1, 'Fifteen minutes': 1, 240: 1, 210: 2,
                                          '1 hour': 2, 241: 2, 242: 2, 243: 2, 244: 3, 245: 3, 211: 3, 246: 3, 247: 3,
                                          248: 3, 249: 3}
        location_type_mapping = {'ANY': 0, 'AT': 1, 'NEAR': 2, 'ON': 3}
        all_vectors = []
        for i, row in self.projects_content.iterrows():
            vector = [self.one_hot_vector(val, mapping) for val, mapping in
                      zip(row, [topic1_mapping, topic2_mapping, location_type_mapping, time_per_participation_mapping])]
            vector = [item for sublist in vector for item in sublist]
            all_vectors.append(vector)

        similarities = cosine_similarity(all_vectors)
        sim = pd.DataFrame(similarities, self.projects_content.index, self.projects_content.index)
        sim.columns = [int(i) for i in sim.columns]
        sim.index = [int(i) for i in sim.index]
        return sim

    # @staticmethod
    # def almost1(arr):
    #     for i in arr:
    #         if i > 0.5:
    #             return True
    #     return False

    def get_recommendations(self, user_index, known_user_projects, k, ip_address):
        relevant_known_projects = list(filter(lambda p: p in self.projects_content.index, known_user_projects))
        topics = self.projects_content.loc[relevant_known_projects]['topic1'].values
        isHybrid = len(relevant_known_projects) != len(known_user_projects) or len(list(filter(lambda topic: topic != topic, topics))) > 0
        if isHybrid:
            return self.hybrid_alg.get_recommendations(user_index, known_user_projects, k, ip_address)
        else:
            user_projects = self.data_matrix[known_user_projects]  # without ratings!!
            neighbourhood_size = 100
            data_neighbours = pd.DataFrame(0, user_projects.columns, range(1, neighbourhood_size + 1))
            for i in range(0, len(user_projects.columns)):
                data_neighbours.iloc[i, :neighbourhood_size] = user_projects.iloc[0:, i].sort_values(0, False)[
                                                               :neighbourhood_size].index

            # Construct the neighbourhood from the most similar items to the
            # ones our user has already liked.
            most_similar_to_likes = data_neighbours.loc[known_user_projects]
            similar_list = most_similar_to_likes.values.tolist()
            similar_list = list(set([item for sublist in similar_list for item in sublist]))
            similar_list = [project for project in similar_list if project in self.data_items.columns[1:]]
            neighbourhood = self.data_matrix[similar_list].loc[similar_list]
            user_vector = self.data_items.loc[user_index].loc[similar_list]
            score = neighbourhood.dot(user_vector).div(neighbourhood.sum(1))
            for project in known_user_projects:
                if project in score.index:
                    score = score.drop(project)
            score = self.remove_non_active_projects(score)
            # score = self.remove_unreachable_projects(score, ip_address)
            self.score = score
            self.user = user_index
            hybrid_recs = self.hybrid_alg.get_recommendations(user_index, known_user_projects, 20, ip_address)
            hybrid_recs = [p for p in hybrid_recs if p in score.index]
            relevant_projects = score.loc[hybrid_recs].nlargest(k).index.tolist()
            return relevant_projects


    @staticmethod
    def remove_non_active_projects(projects_score):
        from Recommender import non_active_projects
        for project in projects_score.index:
            if project in non_active_projects['project'].values:
                projects_score = projects_score.drop(project)
        return projects_score

    @staticmethod
    def remove_unreachable_projects(projects_score, ip_address):
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
