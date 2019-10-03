import abc


class Strategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_recommendations(self, user_index, k, ip_address):
        pass

    @abc.abstractmethod
    def get_highest_online_project(self):
        pass