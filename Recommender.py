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


data = pd.read_pickle('data.pkl')
data_items = data.drop('user', 1)
data_items.columns = [int(x) for x in data_items.columns]
projects_info = pd.read_csv('projects_info.csv', index_col=0)

def get_recommendations(user_index, k, algorithm):
    try:
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
        return recommended_projects
    except Exception as e:
        print ("*****")
        print (e)
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

def main():
    algorithms = [CFItemItem(data_items), CFUserUser(data_items), PopularityBased(data_items), SVD(data_items)]
    for algorithm in algorithms:
        for user_index in data_items.index:
            print(get_recommendations(user_index,3,algorithm))

if __name__ == "__main__":
    main()
