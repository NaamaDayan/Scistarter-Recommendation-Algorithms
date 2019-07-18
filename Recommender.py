import pandas as pd
import logging
import datetime
import random
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


data = pd.read_csv('user_project_matrix.csv')
data_items = data.drop('user', 1)
data_items.columns = [int(x) for x in data_items.columns]
projects_info = pd.read_csv('projects_info.csv', index_col=0)
logging.basicConfig(filename='log_file.log', level=logging.DEBUG)
user_algorithm_mapping = pd.read_csv('user_algorithm_mapping.csv', index_col = 0)

def get_recommendations(user_profile_id, k, algorithm):
    try:
        user_index = data[data['user']==user_profile_id].index[0]
        if len(get_user_projects(user_index)) < 3:  # fresh user
            algorithm = PopularityBased(data_items)
        recommended_projects = algorithm.get_recommendations(user_index, k)
        if not is_online_project_recommended(recommended_projects):
            recommended_projects[-1] = algorithm.get_highest_online_project()
        if len(recommended_projects) < k:
            new_to_recommend = list(PopularityBased(data_items).get_recommendations(user_index, k))
            for project in new_to_recommend:
                if project not in recommended_projects:
                    recommended_projects.append(project)
        json_info = {'user_profile_id':user_profile_id, 'algorithm': algorithm.name, 'recommendations':recommended_projects, 'timestamp':str(datetime.datetime.now())}
        logging.info(json_info)
        return recommended_projects
    except Exception as e:
        logging.error(str(e)+" "+user_profile_id)
        return PopularityBased(data_items).get_recommendations(user_index, k)

def is_online_project(project):
    return projects_info.loc[project]['is_online']

def is_online_project_recommended(recommendations):
    return len([project for project in recommendations if is_online_project(project)]) > 0

def get_online_projects():
    return list(filter(lambda x: is_online_project(x), data_items.columns))

def recommend_default_online(user):
    projects_popularity_scores = data_items.astype(bool).sum(axis=0)
    relevant_projects = get_online_projects()
    relevant_projects = list(filter(lambda x: x not in get_user_projects(user), relevant_projects))
    return projects_popularity_scores.loc[relevant_projects].nlargest(1).index[0]


def map_user_algorithm(user_profile_id):
    try:
        algs = [CFItemItem, CFUserUser, PopularityBased, SVD]
        if user_profile_id in user_algorithm_mapping.index:
            algorithm_id = user_algorithm_mapping.loc[user_profile_id]['algorithm']
        else:
            algorithm_id = random.randint(0,3)
            with open('user_algorithm_mapping.csv', 'w') as file:
                file.write(user_profile_id+","+str(algorithm_id))
        return algs[algorithm_id](data_items)
    except Exception as e:
        logging.error(str(e) + " " + user_profile_id)
        return PopularityBased(data_items)


