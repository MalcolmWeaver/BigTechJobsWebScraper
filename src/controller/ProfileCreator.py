from abc import ABC, abstractmethod

class ProfileCreator(ABC):
    @abstractmethod
    def create_profile(self, user_data: dict) -> object:
        pass