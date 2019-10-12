import pandas as pd
import datetime
import random
import csv
from CFItemItem import CFItemItem
from CFUserUser import CFUserUser
from PopularityBased import PopularityBased
from SVD import SVD
from Baseline import Baseline
from sklearn.feature_extraction.text import TfidfVectorizer
from more_itertools import unique_everseen
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_user_projects(user_id):
    if user_id in data_items.index:
        known_user_likes = data_items.loc[user_id]
        known_user_likes = known_user_likes[known_user_likes > 0].index.values
        return known_user_likes
    return []


data = pd.read_csv('user_project_matrix.csv')
data_items = data.drop('user', 1)
data_items.columns = [int(x) for x in data_items.columns]
projects_info = pd.read_csv('projects_info.csv', index_col=0)
user_algorithm_mapping_df = pd.read_csv('user_algorithm_mapping.csv')
user_algorithm_mapping = {e.user_profile_id: e.algorithm for _, e in user_algorithm_mapping_df.iterrows()}
algorithms = [CFItemItem(data_items), CFUserUser(data_items),  PopularityBased(data_items), SVD(data_items), Baseline()]
non_active_projects = pd.read_csv('non_active_projects.csv')

def get_recommendations(user_profile_id, k, algorithm, ip_address):
    try:
        user_index_place = data[data['user']==user_profile_id].index
        user_index = user_index_place[0] if len(user_index_place)>0 else -1
        if user_index == -1 or len(get_user_projects(user_index)) < 3:  # fresh user
            algorithm = PopularityBased(data_items)
        known_user_projects = get_user_projects(user_index)
        recommended_projects = algorithm.get_recommendations(user_index, known_user_projects, k, ip_address)
        recommended_projects = make_sure_k_recommendations(recommended_projects, user_index, k, ip_address)
        recommended_projects, not_online_recommended_project = make_sure_online_project_exists(recommended_projects, algorithm)
        save_to_log(user_profile_id, algorithm, recommended_projects, not_online_recommended_project, ip_address)
        return recommended_projects
    except Exception as e:
        f = open("log_file.txt", "a")
        f.write(str({"Error":str(e), "user_profile_id":user_profile_id}) + ",\n")
        f.close()
        return PopularityBased(data_items).get_recommendations(-1, [], 3, ip_address)


def save_to_log(user_profile_id, algorithm, recommended_projects, is_online_added, ip_address):
    json_info = {'user_profile_id': user_profile_id, 'algorithm': algorithm.name,
                 'recommendations': recommended_projects, 'timestamp': str(datetime.datetime.now()), 'is_online_added':is_online_added, 'ip_address':ip_address}
    f = open("log_file.txt", "a")
    f.write(str(json_info) + ",")
    f.close()


def make_sure_k_recommendations(recommended_projects, user_index,k,ip_address):
    if len(recommended_projects) < k:
        known_user_projects = get_user_projects(user_index)
        new_to_recommend = list(PopularityBased(data_items).get_recommendations(user_index, known_user_projects, k, ip_address))
        for project in new_to_recommend:
            if project not in recommended_projects:
                recommended_projects.append(project)
    return recommended_projects


def make_sure_online_project_exists(recommendations, algorithm):
    not_online_recommended_project = 0
    if not is_online_project_recommended(recommendations):
        not_online_recommended_project = recommendations[-1]
        recommendations[-1] = algorithm.get_highest_online_project()
    return recommendations, not_online_recommended_project


def is_online_project(project):
    if project in projects_info.index:
        return projects_info.loc[project]['is_online']
    return False


def is_online_project_recommended(recommendations):
    return len([project for project in recommendations if is_online_project(project)]) > 0


def get_online_projects():
    return list(filter(lambda x: is_online_project(x), data_items.columns))


def recommend_default_online(user):
    projects_popularity_scores = data_items.astype(bool).sum(axis=0)
    relevant_projects = get_online_projects()
    relevant_projects = list(filter(lambda x: x not in get_user_projects(user), relevant_projects))
    return projects_popularity_scores.loc[relevant_projects].nlargest(1).index[0]


def user_has_history(user_profile_id):
    if user_profile_id in data['user'].values:
        user_index = data[data['user'] == user_profile_id].index[0]
        if len(get_user_projects(user_index)) > 2:
            return True
    return False


def update_document_id(new_id):
    with open('algorithm_number.txt', "w") as fd:
        fd.write(str(new_id) + "\n")


def retrieve_document_id():
    with open('algorithm_number.txt', "r") as fd:
        return int(fd.readline().strip())


def map_user_algorithm(user_profile_id):
    try:
        if user_has_history(user_profile_id): # user participates in at least 3 projects

            fields = ['user_profile_id', 'algorithm']
            if user_profile_id in user_algorithm_mapping:
                algorithm_id = int(user_algorithm_mapping[user_profile_id])
            else:
                current_algorithm = retrieve_document_id()
                update_document_id(current_algorithm+1)
                algorithm_id = current_algorithm%5
                user_algorithm_mapping[user_profile_id] = algorithm_id
                with open('user_algorithm_mapping.csv', 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fields)
                    row = {'user_profile_id':user_profile_id, 'algorithm': algorithm_id}
                    writer.writerow(row)
            return algorithms[algorithm_id]
    except Exception as e:
        print ("Error:" ,e)
    return algorithms[2] #popularity
