from Strategy import Strategy


class PopularityBased(Strategy):

    def __init__(self, data_items):
        self.name = 'Popularity'
        self.data_items = data_items
        self.projects_popularity_scores = data_items.astype(bool).sum(axis=0)
        self.user = None

    def get_recommendations(self, user_index, k):
        from Recommender import get_user_projects
        known_user_projects = get_user_projects(user_index)
        self.user = user_index
        return list(self.projects_popularity_scores.drop(known_user_projects).nlargest(k).index)

    def get_highest_online_project(self):
        from Recommender import recommend_default_online
        return recommend_default_online(self.user)