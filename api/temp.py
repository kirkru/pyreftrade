# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
from unicodedata import decimal

# marshalling - https://ifitzsimmons.medium.com/automated-dynamodb-data-marshaling-cadb4665a6a0

DDB_PRIMITIVES_MAP = {
  str: 'S',     # DynamoDB String Attribute Type
  int: 'N',     # DynamoDB Number Attribute Type
  float: 'N',   # DynamoDB Number Attribute Type
  bool: 'BOOL', # DynamoDB Boolean Attribute Type
  dict: 'M',    # DynamoDB Dictionary Attribute Type
  list: 'L'     # DynamoDB List Attribute Type
}

# Basic python dictionary, consumable by boto3 higher level API (DynamoDB.Table)
python_data = {
  'obj': {
    'attr1': '1',
    'attr2': [1, 2],
    'attr3': {'hello': 'world'},
    'attr4': True
  }
}

# DynamoDB marshalled item, consumable by boto3 lower level API (DynamoDB)
marshalled_form = {
  'obj': {
    'M': {
      'attr1': {'S': '1'},
      'attr2': {'L': [{'N': '1'}, {'N': '2'}]},
      'attr3': {'M': {'hello': {'S': 'world'}}},
      'attr4': {'BOOL': True}
    }
  }
}

def marshal_object(ddb_item):
    """Convert dicitonary into DynamoDB marshalled item
    >>> marshal_object(1)
    {'N': '1'}
    >>> marshal_object({'item': {'hello': 'world', 'goodnight': 'moon'}})
    {'item': {'M': {'hello': {'S': 'world'}, 'goodnight': {'S': 'moon'}}}}
    Parameters
    ----------
    ddb_item: object
      The data to be converted to a DynamoDB marshalled item.
    Returns
    -------
    marshalled_item: dict
      DynamoDB Marshalled Item.
    """
    marshalled_item = {}
    
    try: 
        for key, value in ddb_item.items():
            marshalled_type = DDB_PRIMITIVES_MAP[type(value)]

            if marshalled_type == 'L':
                marshalled_item[key] = {marshalled_type: []}
                for list_item in value:
                    marshalled_item[key][marshalled_type].append(marshal_object(list_item))
            elif marshalled_type == 'M':
                # recursively marshal dicionary
                marshalled_item[key] = {marshalled_type: marshal_object(value)}
            else:
                # Primitive number, bool, or str
                # Must convert python numbers to strings for DDB consumption
                item_value = value if marshalled_type != 'N' else str(value)
                marshalled_item[key] = {marshalled_type: item_value}
    except AttributeError: 
        # Base Case, item is a primitive.
        marshalled_type = DDB_PRIMITIVES_MAP[type(ddb_item)]
        
        # Must convert python numbers to strings for DDB consumption
        marshalled_item[marshalled_type] = (
            ddb_item if marshalled_type != 'N' else str(ddb_item)
        )
        return marshalled_item
            
    return marshalled_item
    
def unmarshal_response(ddb_response_item):
    """Unmarshals DynamoDB response item into python dictionary

    >>> unmarshal_response({'number': {'N': '1.2'}})
    {'number': 1.2}

    >>> unmarshal_response({'number': {'N': '1'}})
    {'number': 1}

    >>> unmarshal_response({'map': {'M': {'item': {'S': 'string'}}}})
    {'map': {'item': 'string'}}

    >>> unmarshal_response({'list': {'L': [{'S': 'string'}, {'M': {'item': {'S': 'string'}}}]}})
    {'list': ['string', {'item': 'string'}]}

    Parameters
    ----------
    ddb_response_item: dict
      Either the entire DDB response item or an attribute from the response item.

    Returns
    -------
    unmarshalled: dict
      Unmarshalled response.
    """
    unmarshalled = {}

    for key, value in ddb_response_item.items():
        if key in ['S', 'BOOL']:
            return value
        elif key == 'N':
            try:
                return int(value)
            except:
                return float(value)
        elif key == 'M':
            # If the DDB Item is a dict, recursively unpack dict
            return unmarshal_response(value)
        elif key == 'L':
            # If the DDB Item is a list, return unmarshalled value for each item in list
            list_items = []
            for item in value:
                list_items.append(unmarshal_response(item))
            return list_items
        else:
            unmarshalled[key] = unmarshal_response(value)

    return unmarshalled
    
class DictObj:
    def __init__(self, in_dict:dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)
               
              
s = "[{\"quantity\": 2, \"price\": 140, \"symbolId\": \"AAPL\", \"symbolName\": \"Apple Inc.\"}, {\"quantity\": 1, \"price\": 90, \"symbolId\": \"XOM\", \"symbolName\": \"Exxon Mobil Inc.\"}]"

print(s)

reviewOrder = {'userName': 'kir', 'orderItems': '[{"quantity": 2, "price": 140, "symbolId": "AAPL", "symbolName": "Apple Inc."}, {"quantity": 1, "price": 90, "symbolId": "XOM", "symbolName": "Exxon Mobil Inc."}]'}

r2 = {
  "userName": "kir",
  "orderItems": [
    {
      "symbolId": "AAPL",
      "symbolName": "Apple Inc.",
      "quantity": 2,
      "price": 140
    },
    {
      "symbolId": "XOM",
      "symbolName": "Exxon Mobil Inc.",
      "quantity": 1,
      "price": 90
    }
  ]
}

# ddB_reviewOrder = {'userName': 'kir', 'orderItems': '[{"quantity": Decimal('2'), "price": Decimal('140'), "symbolId": "AAPL", "symbolName": "Apple Inc."}]'}

mro = marshal_object(reviewOrder)

print("MRO: ", mro)

mro2 = marshal_object(r2)

print("MRO2: ", mro2)

ddb1 = {'userName': {'S': 'kir'}, 'orderItems': {'L': [{'symbolId': {'S': 'AAPL'}, 'symbolName': {'S': 'Apple Inc.'}, 'quantity': {'N': '2'}, 'price': {'N': '140'}}, {'symbolId': {'S': 'XOM'}, 'symbolName': {'S': 'Exxon Mobil Inc.'}, 'quantity': {'N': '1'}, 'price': {'N': '90'}}]}}

r1 = unmarshal_response(ddb1)
print ("r1: ", r1 )
print(type(reviewOrder))

reviewOrderRequest = DictObj(reviewOrder)

print(reviewOrderRequest)

print(reviewOrderRequest.userName)

print(reviewOrderRequest.orderItems)

dictOrderItems = eval(reviewOrderRequest.orderItems)
# print(dictOrderItems)

for item in dictOrderItems:
    print(item["price"])
    
# {
#   "userName": "kir",
#   "orderItems": "[{\"quantity\": 2, \"price\": 140, \"symbolId\": \"AAPL\", \"symbolName\": \"Apple Inc.\"}, {\"quantity\": 1, \"price\": 90, \"symbolId\": \"XOM\", \"symbolName\": \"Exxon Mobil Inc.\"}]"
# }
# print(dictOrderItems[0])


dictReviewOrder = {
  "userName": "kir",
  "orderItems": [
    {
      "symbolId": "AAPL",
      "symbolName": "Apple Inc.",
      "quantity": 2,
      "price": 140
    },
    {
      "symbolId": "XOM",
      "symbolName": "Exxon Mobil Inc.",
      "quantity": 1,
      "price": 90
    }
  ]
}

print("======")

for item in dictReviewOrder["orderItems"]:
    print(item["price"])

# objorderItems()    

print("======")
objReviewOrder2 = DictObj(dictReviewOrder)
print(objReviewOrder2.orderItems[0].price * objReviewOrder2.orderItems[0].quantity)

totalPrice = 0.0
print(totalPrice)

# objReviewOrder = DictObj(reviewOrder)

# orderPayload = reviewOrder
# for ob in reviewOrder['orderItems']:
# for orderItem in reviewOrder["orderItems"]:
#   totalPrice = totalPrice + (decimal.Decimal(orderItem["price"]) * orderItem["quantity"])
# print(totalPrice)
for orderItem in objReviewOrder2.orderItems:
    totalPrice = totalPrice + (orderItem.quantity * orderItem.price)

print(totalPrice)
  
# objOrderItems = DictObj(dictOrderItems)
# print(objOrderItems)
# for ob in objOrderItems:
#     print(ob.price)
    

# d = eval(s)
# print(d)
# print(d[0])
# print(d[0].get("quantity"))

# d = decimal(0)
# d = decimal((float(0.0)))
d = float(2.0)
q = 2.0
p = 10.0
t = d + (q*p)
