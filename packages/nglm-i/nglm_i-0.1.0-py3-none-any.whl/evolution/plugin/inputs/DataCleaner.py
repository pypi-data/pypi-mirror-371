from abc import abstractmethod, ABC
class DataCleaner(ABC):

    @abstractmethod
    def clean_data(self, data_frame):
        pass
