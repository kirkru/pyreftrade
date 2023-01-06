from pydantic import BaseModel
from typing import Optional
from typing import List, Any

# class DictObj:
#     def __init__(self, in_dict:dict):
#         assert isinstance(in_dict, dict)
#         for key, val in in_dict.items():
#             if isinstance(val, (list, tuple)):
#                setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
#             else:
#                setattr(self, key, DictObj(val) if isinstance(val, dict) else val)            

# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         # 👇️ if passed in object is instance of Decimal
#         # convert it to a string
#         if isinstance(obj, Decimal):
#             return str(obj)
#         # 👇️ otherwise use the default behavior
#         return json.JSONEncoder.default(self, obj)

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

class ReviewOrderRequest(BaseModel):
    userName: str
    accountId: str
    totalPrice: Optional[float] = 0.0
    orderItems: List[OrderItem]

    @staticmethod
    def from_dict(obj: Any) -> 'ReviewOrderRequest':
        print("Inside from dict")
        _userName = str(obj.get("userName"))
        _accountId = str(obj.get("accountId"))

        print(_userName, _accountId)
        _totalPrice = float(obj.get("totalPrice"))
        _orderItems = [OrderItem.from_dict(y) for y in obj.get("orderItems")]
        print(_orderItems)
        return ReviewOrderRequest(_userName, _orderItems, _totalPrice, _accountId)
