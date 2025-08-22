from evolution.plugin.inputs.DataExplorer import DataExplorer


class QADataExplorer(DataExplorer):

    def explore_data(self, data_frame):
        print("qa explorer exploring data")
        return data_frame