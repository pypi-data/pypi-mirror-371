from abc import ABC, abstractmethod
from typing import Optional

class IRealTimeQuoteProvider(ABC):
    '''interface for getting real time quote/price for a symbol'''
    @abstractmethod
    def get_price(self, symbol: str) -> Optional[float]:
        raise NotImplementedError('not implemented in interface')