from collections import _OrderedDictItemsView
import os
import time
from unicodedata import decimal
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

app = FastAPI()
handler = Mangum(app)

# TODO
# get sectors - added a global secondary index
# support /update_symbol

# DONE
# Create Datamodel
# update signatures, implementations of methods
# support lower case sector, ticker
# get symbols by sector


'''
{
  "userName": "kir",
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

# # @dataclass
class OrderItem(BaseModel):
    quantity: int
    price: int
    symbolId: str
    symbolName: str

    @staticmethod
    def from_dict(obj: Any) -> 'OrderItem':
        _quantity = int(obj.get("quantity"))
        _price = int(obj.get("price"))
        _symbolId = str(obj.get("symbolId"))
        _symbolName = str(obj.get("symbolName"))
        return OrderItem(_quantity, _price, _symbolId, _symbolName)

# @dataclass
class ReviewOrderRequest(BaseModel):
    userName: str
    orderItems: List[OrderItem]

    @staticmethod
    def from_dict(obj: Any) -> 'ReviewOrderRequest':
        _userName = str(obj.get("userName"))
        _orderItems = [OrderItem.from_dict(y) for y in obj.get("orderItems")]
        return ReviewOrderRequest(_userName, _orderItems)


@app.get("/")
async def root():
    return {"message": "Hello from ReviewOrder API!"}

@app.put("/create-reviewOrder")
async def create_reviewOrder(reviewOrderRequest: ReviewOrderRequest):
    createdTime = int(time.time())
    print(reviewOrderRequest)
    print(type(reviewOrderRequest))
    print(reviewOrderRequest.orderItems)
    # jsonstring = json.loads(json.dumps(reviewOrderRequest))
    # reviewOrderRequestItem = ReviewOrderRequest.from_dict(jsonstring)
    # print("This is the review item from json")
    # print(reviewOrderRequestItem)


    item = {
        "userName": reviewOrderRequest.userName,
        "createdTime": createdTime,
        "orderItems": json.dumps(reviewOrderRequest.orderItems.__dict__),
        # "orderItems": reviewOrderRequestItem,
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"order": item}

def _get_table():
    table_name = os.environ.get("REVIEWORDER_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
