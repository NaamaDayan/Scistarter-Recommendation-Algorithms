from Location_based_features import is_project_reachable_to_user, get_user_loc
from Strategy import Strategy


class PopularityBased(Strategy):

    def __init__(self, data_items):
        self.name = 'Popularity'
        self.data_items = data_items
        self.projects_popularity_scores = data_items.astype(bool).sum(axis=0)
        self.user = None

    def get_recommendations(self, user_index, known_user_projects, k, ip_address):
        self.user = user_index
        projects_score = self.projects_popularity_scores.drop(known_user_projects)
<<<<<<< HEAD
        projects_score = self.remove_non_active_projects(projects_score)
=======
        projects_score = self.remove_non_active_projects(projects_score) # and non affiliate projects!!!
>>>>>>> master
        # projects_score = self.remove_unreachable_projects(projects_score, ip_address)
        return list(projects_score.nlargest(k).index)

    def remove_non_active_projects(self, projects_score):
        from Recommender import non_active_projects
        from Updater import projects_names
        for project in projects_score.index:
            if project in non_active_projects['project'].values or project not in projects_names.index:
                projects_score = projects_score.drop(project)
        return projects_score

    def remove_unreachable_projects(self, projects_score, ip_address):
        user_loc = get_user_loc(ip_address)
        for project in projects_score.index:
            if not is_project_reachable_to_user(user_loc, project):
                projects_score = projects_score.drop(project)
        return projects_score

    def get_highest_online_project(self):
        from Recommender import recommend_default_online
        return recommend_default_online(self.user)