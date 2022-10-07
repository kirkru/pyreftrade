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

@app.get("/")
async def root():
    return {"message": "Hello from Ordering API!"}

def _get_table():
    table_name = os.environ.get("ORDERING_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
