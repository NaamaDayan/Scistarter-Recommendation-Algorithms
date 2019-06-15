import pandas as pd
from CFUserUser import CFUserUser
from CFItemItem import CFItemItem
from PopularityBased import PopularityBased
from SVD import SVD

data = pd.read_csv('user_project_matrix.csv')
data_items = data.drop('user', 1)


def get_user_projects(user_id):
    known_user_likes = data_items.loc[user_id]
    known_user_likes = known_user_likes[known_user_likes > 0].index.values
    return known_user_likes


def main():
    # example
    user_index = 68684
    k = 5
    algorithm = CFUserUser(data_items)
    # verification stage:
    if len(get_user_projects(user_index)) < 3:  # fresh user
        algorithm = PopularityBased(data_items)
    recommended_projects = algorithm.get_recommendations(user_index, k)
    return recommended_projects


if __name__ == "__main__":
    main()
