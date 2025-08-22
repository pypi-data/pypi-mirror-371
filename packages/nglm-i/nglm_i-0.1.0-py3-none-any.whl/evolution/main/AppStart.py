import importlib

from evolution.plugin.inputs.DataExplorer import DataExplorer
from evolution.plugin.inputs.DataCleaner import DataCleaner
from evolution.plugin.inputs.file.FileInputDataReader import FileInputDataReader
from evolution.plugin.inputs.InputDataReader import InputDataReader

def load_class(cleaner_package: str, cleaner_class: str, class_ref: type):
    try:
        module = importlib.import_module(cleaner_package)
        the_class = getattr(module, cleaner_class)
        the_instance = the_class()
        if isinstance(the_instance, class_ref):
            print("plugin successfully loaded", the_instance.__class__)
            return the_instance
        else:
            print("unable to load plugin {}, expected {}".format(cleaner_package, class_ref))
    except(ModuleNotFoundError, ImportError) as e:
        print(e)




class AppStart:
    input_data_reader: InputDataReader = None
    data_cleaner: DataCleaner = None
    data_explorer: DataExplorer = None
    config: dict = None

    def __init__(self, config: dict):
        self.config = config
        input_type = self.config["input_type"]
        if input_type == 'file':
            self.input_data_reader = load_class('evolution.plugin.inputs.file.FileInputDataReader', 'FileInputDataReader', FileInputDataReader);
        else:
            self.input_data_reader = load_class('evolution.plugin.inputs.file.FileInputDataReader', 'FileInputDataReader', FileInputDataReader);
        self.input_data_reader.load_configs(config)

        self.load_plugins()
        print("plugins loaded")

    def load_plugins(self):
        self.data_cleaner = load_class(self.config["cleaner_package"], self.config["cleaner_class"], DataCleaner)
        self.data_explorer = load_class(self.config["explorer_package"], self.config["explorer_class"], DataExplorer)

    def clean_data(self, dataframe):
        return self.data_cleaner.clean_data(dataframe)

    def explore_data(self, dataframe):
        return self.data_explorer.explore_data(dataframe)



    def validate_data(self, dataframe):
        print("validating data - final dataframe")
        print(dataframe)

    def run(self):
        self.input_data_reader.read_data()
        data_frame = self.input_data_reader.get_data()
        data_frame = self.clean_data(data_frame)
        data_frame = self.explore_data(data_frame)
        self.validate_data(data_frame)
        print("all done")
        pass


#app_start = AppStart("file1")
#app_start.run()

