import pandas as pd
from CFUserUser import CFUserUser
from CFItemItem import CFItemItem
from PopularityBased import PopularityBased
from SVD import SVD


def main():
    data = pd.read_csv('users_projects_full.csv')
    data_items = data.drop('user', 1)
    # example
    user_index = 68684
    k = 5
    algorithm = CFUserUser(data_items)
    recommended_projects = algorithm.get_recommendations(user_index, k)
    return recommended_projects


if __name__ == "__main__":
    main()
