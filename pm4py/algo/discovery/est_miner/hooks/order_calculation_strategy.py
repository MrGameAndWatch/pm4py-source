import abc

class OrderCalculationStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(self, log):
        """
        Calculate two orders on the given log, one for 
        input and one for out activities.
        """
        pass

class NoOrderCalculationStrategy(OrderCalculationStrategy):

    def execute(self, log):
        print('Executed Order Calculation')
        return None, None
