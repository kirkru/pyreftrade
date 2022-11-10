import os
# from unicodedata import decimal
# from urllib.request import Request
import boto3
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key
from dataclasses import dataclass
from typing import List
from typing import Any
import json
from decimal import Decimal
from datetime import datetime, timezone
import uuid

# import traceback
# from bunch import bunchify

app = FastAPI()
handler = Mangum(app)

# TODO
# datamodel finalize
# add accountId sort key, may be?
# get review order by ID?

# price float
# Create Datamodel for SendOrderEvent

'''
{
  "userName": "kir",
  "accountId": "acc123",
  "totalPrice": 0.0,
  "orderItems": [
    {
      "quantity": 2,
      "price": 140,
      "instrumentId": "AAPL",
      "instrumentName": "Apple Inc."
    },
    {
      "quantity": 1,
      "price": 90,
      "instrumentId": "XOM",
      "instrumentName": "Exxon Mobil Inc."
    }
  ]
}
'''

class DictObj:
    def __init__(self, in_dict:dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)            

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)

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

@app.get("/")
async def root():
  # print(request)
  # print(request.query_params)
  return {"message": "Hello from ReviewOrder API!"}

@app.put("/create-reviewOrder")
async def create_reviewOrder(reviewOrderRequest: ReviewOrderRequest):
# async def create_reviewOrder(reviewOrderRequest):
  try:

    # Create the reviewOrder for the user

    # createdTime = int(time.time())
    reviewOrderTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(reviewOrderRequest)
    print(type(reviewOrderRequest))
    print(reviewOrderRequest.orderItems)
    print(type(reviewOrderRequest.orderItems))
    
    # item = marshal_object(reviewOrderRequest)
    item = {
        "reviewOrderId": str(uuid.uuid4()),
        "userName": reviewOrderRequest.userName.lower(),
        "accountId": reviewOrderRequest.accountId,
        "reviewOrderTime": reviewOrderTime,
        "totalPrice": Decimal(str(reviewOrderRequest.totalPrice)),
        "orderItems": json.loads(json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]), parse_float=Decimal),
        # "orderItems": json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]),
    }

    # Put item into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"reviewOrder": item}

  except Exception as e:
    print("Exception occured:", e)
    return {"Exception occured": str(e) }

@app.get("/get-reviewOrder/{userName}")
async def get_reviewOrder(userName: str):
    # Get the reviewOrder from the table for userName.
    table = _get_table()
    response = table.get_item(Key={"userName": userName.lower()})
    print(response)
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"ReviewOrder for User: {userName} not found")
    return item

@app.delete("/delete-reviewOrder/{userName}")
async def delete_reviewOrder(userName: str):
    # Delete the reviewOrder for the user from the table.
    table = _get_table()

    try:
      # response = table.delete_item(Key={"userName": userName})
      # Delete only if item found for user using ConditionalExpression
      response = table.delete_item(Key={"userName": userName}, ConditionExpression="attribute_exists(userName)")
      print (response)
      print (type(response))
    except Exception as e :
      print ("An exception occured")
      print(e)
      # raise HTTPException(status_code=404, detail=f"ReviewOrder for User: {userName} not found")

    return {"deleted_userName_reviewOrder": userName}

@app.put("/sendOrder/{userName}")
async def sendOrder(userName: str):
  print("1 - Getting existing reviewOrder with items")

  reviewOrder = await get_reviewOrder(userName)

  print("Review Order: ", reviewOrder)

  print("2 - create an event json object with reviewOrder items")

  # reviewOrderRequest = ReviewOrderRequest.from_dict(reviewOrder)
  # orderPayload, totalPrice = prepareOrderPayload(reviewOrder)
  orderPayload = prepareOrderPayload(reviewOrder)

  print (orderPayload)

  # print(totalPrice)

  print("3 - publish an event to EventBridge")
  publishedEvent = await publishSendOrderEvent(orderPayload)

  # TODO - upon successfully publishing, delete reviewOrder
  # TODO - update delete reviewOrder with accountID

  print("4 - remove existing reviewOrder")
  await delete_reviewOrder(userName)

  return {"Success":"Sent order to the event bus"}

def prepareOrderPayload(reviewOrder):
  print("prepareOrderPayload")

  try:
    totalPrice = Decimal('0.0')
    #  Convert to Object
    objReviewOrder = DictObj(reviewOrder)

    # Calculate total price
    for orderItem in objReviewOrder.orderItems:
      totalPrice = totalPrice + (orderItem.quantity * orderItem.price)

    print(totalPrice)

    totalPriceDict = {'totalPrice': totalPrice}
    reviewOrder.update(totalPriceDict)

    setattr(objReviewOrder, "totalPrice" , totalPrice)

    # reviewOrder.totalPrice = totalPrice

    # copy all properties from reviewOrder into checkoutRequest

    # orderPayload.__dict__ = reviewOrder.__dict__.copy() 
    # return reviewOrder, totalPrice
    # return objReviewOrder.__dict__
    return reviewOrder

  except Exception as e:
      print ("An exception occured")
      print(e)
      # print(traceback.format_exc())

  '''
    console.log("sendOrder");

  // expected request payload : { userName : vgt, attributes[firstName, lastName, email ..] 
  const checkoutRequest = JSON.parse(event.body);
  if (checkoutRequest == null || checkoutRequest.userName == null) {
    throw new Error(`userName should exist in checkoutRequest: "${checkoutRequest}"`);
  }  
  
  // 1- Get existing reviewOrder with items
  const reviewOrder = await getReviewOrder(checkoutRequest.userName);

  // 2- create an event json object with reviewOrder items, 
    // calculate totalprice, prepare order create json data to send ordering ms 
  var checkoutPayload = prepareOrderPayload(checkoutRequest, reviewOrder);

  // 3- publish an event to eventbridge - this will subscribe by order microservice and start ordering process.
  const publishedEvent = await publishSendOrderEvent(checkoutPayload);

  // 4- remove existing reviewOrder
  await deleteReviewOrder(checkoutRequest.userName);
  '''

async def publishSendOrderEvent(orderPayload):
  print("Publishing the sendOrder event with: ", orderPayload)
  # dictOrderPayload = orderPayload.__dict__
  try:
    print("Before params")

    eventBusParams = {
                'Source':os.environ.get("EVENT_SOURCE"),
                'DetailType':os.environ.get("EVENT_DETAILTYPE"),
                'Detail':json.dumps(orderPayload, indent=4, cls=DecimalEncoder),
                # 'Detail':json.dumps(orderPayload),
                'EventBusName':os.environ.get("EVENT_BUSNAME")
            }

    print("After params")

    client = boto3.client('events')

    response = client.put_events(
        Entries=[eventBusParams]
    )
    print("Sucess: Event Sent. Got response: {}", response)
    return response
  except Exception as e:
    print("Exception occured", e)
    raise HTTPException(status_code=500, detail=f"Exception occured while publishing order event")


def _get_table():
    table_name = os.environ.get("REVIEWORDER_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
