from evolution.plugin.inputs.DataCleaner import DataCleaner


class QACleaner(DataCleaner):

    def clean_data(self, data_frame):
        print("qa cleaner cleaning data")
        return data_frame