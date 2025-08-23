from abc import ABC, abstractmethod


class AbstractNotificationService(ABC):
    """
    Abstract class that defines the basic structure of all notification channels
    """

    @abstractmethod
    def send(self, message, recipients=None, **kwargs):
        pass
