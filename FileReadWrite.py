import os
import pandas as pd

class FileReadWrite:
    def __init__(self, file_name):
        self.file_name = file_name

    def exists(self):
        return os.path.isfile(self.file_name)

    def get_data_csv(self):
        return pd.read_csv(self.file_name)

    def get_data_pkl(self):
        return pd.read_pickle(self.file_name)

    def put_data_csv(self, data):
        data.to_csv(self.file_name, index=False)
        return 1

    def put_data_pkl(self, data):
        data.to_pickle(self.file_name)
