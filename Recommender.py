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


def get_recommendations(user_index, k, algorithm):
    try:
        if len(get_user_projects(user_index)) < 3:  # fresh user
            algorithm = PopularityBased(data_items)
        recommended_projects = algorithm.get_recommendations(user_index, k)
        if len(recommended_projects) < k:
            new_to_recommend = list(PopularityBased(data_items).get_recommendations(user_index, k))
            for project in new_to_recommend:
                if project not in recommended_projects:
                    recommended_projects.append(project)
        return recommended_projects
    except Exception as e:
        print (e)
        return PopularityBased(data_items).get_recommendations(user_index, k)

def main():
    user_index = 32
    k = 3
    algorithm = CFItemItem(data_items)# CFUserUser(data_items)
    print (get_recommendations(user_index, k, algorithm))
    print (get_recommendations(user_index, k, CFUserUser(data_items)))


if __name__ == "__main__":
    main()
