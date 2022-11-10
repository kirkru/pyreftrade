from collections import _OrderedDictItemsView
import os
from queue import Empty
import time
import traceback
from unicodedata import decimal
from urllib.request import Request
import boto3
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key
from dataclasses import dataclass
from typing import List
from typing import Any
import json
import decimal
from decimal import Decimal
from datetime import datetime, timezone
# import traceback
# from bunch import bunchify

app = FastAPI()
handler = Mangum(app)

# TODO
# price float
# Create Datamodel for SendOrderEvent

'''
{
  "userName": "kir",
  "totalPrice": 0.0,
  "orderItems": [
    {
      "quantity": 2,
      "price": 140,
      "symbolId": "AAPL",
      "symbolName": "Apple Inc."
    },
    {
      "quantity": 1,
      "price": 90,
      "symbolId": "XOM",
      "symbolName": "Exxon Mobil Inc."
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
    quantity: int
    price: int
    symbolId: str
    symbolName: str

    @staticmethod
    def from_dict(obj: Any) -> 'OrderItem':
        # obj = ast.literal_eval(obj)
        print("Object passed: ", obj)
        obj = eval(obj)
        _quantity = int(obj.get("quantity"))
        _price = int(obj.get("price"))
        _symbolId = str(obj.get("symbolId"))
        _symbolName = str(obj.get("symbolName"))
        return OrderItem(_quantity, _price, _symbolId, _symbolName)

class ReviewOrderRequest(BaseModel):
    userName: str
    totalPrice: Optional[float] = 0.0
    orderItems: List[OrderItem]

    @staticmethod
    def from_dict(obj: Any) -> 'ReviewOrderRequest':
        print("Inside from dict")
        _userName = str(obj.get("userName"))
        print(_userName)
        _totalPrice = float(obj.get("totalPrice"))
        _orderItems = [OrderItem.from_dict(y) for y in obj.get("orderItems")]
        print(_orderItems)
        return ReviewOrderRequest(_userName, _orderItems)

@app.get("/")
async def root(request: Request):
  print(request)
  print(request.query_params)
  return {"message": "Hello from ReviewOrder API!"}

@app.put("/create-reviewOrder")
async def create_reviewOrder(reviewOrderRequest: ReviewOrderRequest):
# async def create_reviewOrder(reviewOrderRequest):

    # Create the reviewOrder for the user

    # createdTime = int(time.time())
    reviewOrderTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(reviewOrderRequest)
    print(type(reviewOrderRequest))
    print(reviewOrderRequest.orderItems)
    print(type(reviewOrderRequest.orderItems))
    
    # item = marshal_object(reviewOrderRequest)
    item = {
        "userName": reviewOrderRequest.userName.lower(),
        "reviewOrderTime": reviewOrderTime,
        "totalPrice": Decimal(str(reviewOrderRequest.totalPrice)),
        "orderItems": [ob.__dict__ for ob in reviewOrderRequest.orderItems],
        # "orderItems": json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]),
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"order": item}

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

  print("Review Order: {}", reviewOrder)

  print("2 - create an event json object with reviewOrder items")

  # reviewOrderRequest = ReviewOrderRequest.from_dict(reviewOrder)
  # orderPayload, totalPrice = prepareOrderPayload(reviewOrder)
  orderPayload = prepareOrderPayload(reviewOrder)

  print (orderPayload)

  # print(totalPrice)

  print("3 - publish an event to EventBridge")
  publishedEvent = await publishSendOrderEvent(orderPayload)

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
    setattr(objReviewOrder, "totalPrice" , totalPrice)

    # reviewOrder.totalPrice = totalPrice

    # copy all properties from reviewOrder into checkoutRequest

    # orderPayload.__dict__ = reviewOrder.__dict__.copy() 
    # return reviewOrder, totalPrice
    return objReviewOrder

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
  dictOrderPayload = orderPayload.__dict__
  try:
    eventBusParams = {
                'Source':os.environ.get("EVENT_SOURCE"),
                'DetailType':os.environ.get("EVENT_DETAILTYPE"),
                'Detail':json.dumps(dictOrderPayload, indent=4, cls=DecimalEncoder),
                # 'Detail':json.dumps(orderPayload),
                'EventBusName':os.environ.get("EVENT_BUSNAME")
            }

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
