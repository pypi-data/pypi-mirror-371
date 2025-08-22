from abc import abstractmethod, ABC

class DataExplorer(ABC):

    @abstractmethod
    def explore_data(self, data_frame   ):
        pass
