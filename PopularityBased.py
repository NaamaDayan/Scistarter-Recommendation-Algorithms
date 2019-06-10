from Strategy import Strategy


class PopularityBased(Strategy):

    def __init__(self, data_items):
        self.data_items = data_items
        self.projects_popularity_scores = data_items.astype(bool).sum(axis=0)

    def get_recommendations(self, user_index, k):
        return self.projects_popularity_scores.nlargest(k).index
