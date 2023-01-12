from pydantic import BaseModel
from typing import Optional
from typing import List, Any

class OrderItem(BaseModel):
    quantity: float
    price: float
    instrumentId: str
    instrumentName: str

    @staticmethod
    def from_dict(obj: Any) -> 'OrderItem':
        # obj = ast.literal_eval(obj)
        print("Object passed: ", obj)
        obj = eval(obj)
        _quantity = float(obj.get("quantity"))
        _price = float(obj.get("price"))
        _instrumentId = str(obj.get("instrumentId"))
        _instrumentName = str(obj.get("instrumentName"))
        return OrderItem(_quantity, _price, _instrumentId, _instrumentName)

class TradeRequest(BaseModel):
    accountId: str
    tradeId: Optional[str]
    tradeProcessedTime: Optional[str]
    userName: str
    reviewOrderTime: str
    reviewOrderId: str
    totalPrice: Optional[float]
    tradeItems: List[OrderItem]
