import numpy as np
import pandas as pd
from more_itertools import unique_everseen
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Recommender
from CFItemItem import CFItemItem
from CFUserUser import CFUserUser
from PopularityBased import PopularityBased
from ContentBased import ContentBased
from Recommender import is_online_project_recommended
from SVD import SVD

projects_data = pd.read_csv('projects_data.csv', index_col=0)
projects_data = projects_data.fillna('')
records = pd.read_pickle('historical_records.pkl')
data_items_train = pd.read_pickle('data_items_train.pkl')


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


data_matrix = calculate_similarity_by_content()


def calc_special_precision(relevant_projects, known_user_likes_test):
    known_user_likes_test = [int(x) for x in known_user_likes_test]
    precision = np.intersect1d(relevant_projects, known_user_likes_test).size / len(relevant_projects)
    rejected_recs = list(set(relevant_projects) - set(known_user_likes_test))
    similarity_sums = np.sum([calc_max_sim(rp, known_user_likes_test) for rp in rejected_recs])
    return precision + similarity_sums / len(relevant_projects)


def calc_max_sim(rejected_project, chosen_projects):
    sim = []
    for cp in chosen_projects:
        if str(cp) in data_matrix.index and str(rejected_project) in data_matrix.index:
            sim.append(data_matrix.loc[str(cp)][str(rejected_project)])
        else:
            sim.append(0)
    return np.max(sim)


def get_precision_and_recall_by_time_split(user, k, algorithm, ip_address):
    user_data = records[records.profile == user]
    projects_list = list(user_data['project'].values)
    projects_list = [str(int(x)) for x in projects_list if x is not None and x==x]
    projects_list = list(unique_everseen(projects_list))
    projects_list = [int(x) for x in projects_list]
    if len(projects_list)>= Recommender.HISTORY_THRES:
        splitter_index = max(1, int(0.9*len(projects_list)))
        # split to train and test by timeline!!
        known_user_likes_train = projects_list[:splitter_index]
        known_user_likes_test = projects_list[splitter_index:]
        user_index_place = Recommender.data[Recommender.data['user'] == user].index
        user_index = user_index_place[0] if len(user_index_place) > 0 else -1

        relevant_projects = algorithm.get_recommendations(user_index, known_user_likes_train, k, ip_address)
        # precision = len([project for project in known_user_likes_test if project in relevant_projects]) / len(known_user_likes_test)
        # print ("precision:", precision)
        relevant_projects = Recommender.make_sure_k_recommendations(relevant_projects, user_index, k, ip_address)
        print (user, relevant_projects, known_user_likes_test)
        # if not is_online_project_recommended(relevant_projects):
        #     relevant_projects[-1] = algorithm.get_highest_online_project()
        # print ("recommendations: ", relevant_projects)
        if len(relevant_projects)<k: #for debugging
            print ("problem with user: ", user_index)
        # calculate recall and precision - this is the same value since the sets are the same size
        precision = np.intersect1d(relevant_projects, known_user_likes_test).size / len(relevant_projects)
        special_percision = calc_special_precision(relevant_projects, known_user_likes_test)
        recall = np.intersect1d(relevant_projects, known_user_likes_test).size / len(known_user_likes_test)
        return [precision,recall, special_percision]
    return [-1, -1, -1]


def precision_recall_at_k(k_values, test_users, algorithm):
    for k in k_values:
        results = []
        ip_addresses = ['']
        i=0
        for user in test_users:
            print (i)
            results.append(get_precision_and_recall_by_time_split(user, k, algorithm, ip_addresses[i%len(ip_addresses)]))
            i+=1
        precisions = np.mean([i[0] for i in results if i[0]>=0])
        recalls = np.mean([i[1] for i in results if i[1]>=0])
        special_precisions = np.mean([i[2] for i in results if i[2]>=0])
        print (precisions, recalls, special_precisions)


if __name__ == '__main__':
    print(Recommender.data_items.shape)
    print(data_items_train.shape)

    # for ip change get_recommendation param
    precision_recall_at_k([3], Recommender.data['user'].values, ContentBased(data_items_train, PopularityBased(data_items_train)))
    # precision_recall_at_k([3], Recommender.data['user'].values, CFItemItem(data_items_train))
    # precision_recall_at_k([3], Recommender.data['user'].values, CFUserUser(data_items_train))
    # precision_recall_at_k([3], Recommender.data['user'].values, PopularityBased(data_items_train))
    # precision_recall_at_k([3], Recommender.data['user'].values, SVD(data_items_train))