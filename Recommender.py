import pandas as pd

from CFItemItem import CFItemItem
from CFUserUser import CFUserUser
from PopularityBased import PopularityBased
from SVD import SVD
from sklearn.feature_extraction.text import TfidfVectorizer
from more_itertools import unique_everseen
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_user_projects(user_id):
    known_user_likes = data_items.loc[user_id]
    known_user_likes = known_user_likes[known_user_likes > 0].index.values
    return known_user_likes


def get_precision_and_recall_by_time_split(user_index, k, algorithm):
    user = data.loc[user_index][0]
    user_data = records[records.profile == user]
    projects_list = list(user_data['project'].values)
    projects_list = [str(int(x)) for x in projects_list if x is not None and x==x]
    projects_list = list(unique_everseen(projects_list))
    if len(projects_list)>2:
        splitter_index = max(1, int(0.9*len(projects_list)))
        # split to train and test by timeline!!
        known_user_likes_train = projects_list[:splitter_index]
        known_user_likes_test = projects_list[splitter_index:]
        relevant_projects = algorithm.get_recommendations(user_index, known_user_likes_train, k)
        print (relevant_projects)
        # calculate recall and precision - this is the same value since the sets are the same size
        precision = np.intersect1d(relevant_projects, known_user_likes_test).size / len(relevant_projects)
        special_percision = calc_refined_precision(relevant_projects, known_user_likes_test)
        recall = np.intersect1d(relevant_projects, known_user_likes_test).size / len(known_user_likes_test)
        return [precision, recall, special_percision]
    return [-1, -1, -1]


def calc_refined_precision(relevant_projects, known_user_likes_test):
    precision = np.intersect1d(relevant_projects, known_user_likes_test).size / len(relevant_projects)
    rejected_recs = list(set(relevant_projects) - set(known_user_likes_test))
    similarity_sums = np.sum([calc_max_sim(rp, known_user_likes_test) for rp in rejected_recs])
    return precision + similarity_sums / len(relevant_projects)


def calc_max_sim(rejected_project, chosen_projects):
    return np.max([data_matrix.loc[cp][rejected_project] for cp in chosen_projects])


def precision_recall_at_k(k_values, test_users, algorithm):
    for k in k_values:
        results = []
        for user in test_users:
            results.append(get_precision_and_recall_by_time_split(user, k, algorithm))
        precisions = np.mean([i[0] for i in results if i>=0])
        recalls = np.mean([i[1] for i in results if i>=0])
        special_precisions = np.mean([i[2] for i in results if i>=0])
        print (precisions, recalls, special_precisions)


def calculate_similarity_by_content():
    tf_idf = TfidfVectorizer()
    total_similarity = pd.DataFrame(0, index=range(len(projects_data)), columns=range(len(projects_data)))
    for feature in projects_data.columns:
        feature_similarity = tf_idf.fit_transform(projects_data[feature])
        feature_similarity = pd.DataFrame(cosine_similarity(feature_similarity))
        total_similarity = total_similarity + feature_similarity / 4  # check the division!!!
    total_similarity.index = [str(i) for i in projects_data.index]
    total_similarity.columns = [str(i) for i in projects_data.index]
    return total_similarity


data = pd.read_csv('user_project_matrix.csv')
data_items = data.drop('user', 1)
records = pd.read_pickle('records.pkl')
projects_data = pd.read_csv('projects_meta_data_4_attr.csv', index_col=0)
projects_data = projects_data.fillna('')
data_matrix = calculate_similarity_by_content()


def main():
    # example
    user_index = 68684
    k = 5
    algorithm = CFItemItem(data_items) # CFUserUser(data_items)
    # verification stage:
    if len(get_user_projects(user_index)) < 3:  # fresh user
        algorithm = PopularityBased(data_items)
    recommended_projects = algorithm.get_recommendations(user_index, k)
    print (recommended_projects)
    algorithm = CFUserUser(data_items)
    recommended_projects = algorithm.get_recommendations(user_index, k)
    print (recommended_projects)
    return recommended_projects


if __name__ == "__main__":
    main()
