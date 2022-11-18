from collections import _OrderedDictItemsView
import os
import time
from unicodedata import decimal
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

from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI Mangum Example")

# TODO: Add these lines
app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["x-apigateway-header", "Content-Type", "X-Amz-Date"],
)

# app = FastAPI()
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

{
  "version": "0",
  "id": "0e7baf25-3f8f-08b9-589b-c047c6802947",
  "detail-type": "reveiwOrder",
  "source": "com.vg.reftra.reveiwOrder",
  "account": "103384195692",
  "time": "2022-10-17T21:27:15Z",
  "region": "us-west-2",
  "resources": [],
  "detail": {
    "username": "tester",
    "total": "200"
  }
}

Eventbus Rule Event Pattern

{
  "detail-type": ["tr_SendOrder"],
  "source": ["com.vgt.reviewOrder.sendOrder"]
}

'''

import json

# def handler(event, context):
#     print('request: {}'.format(json.dumps(event)))
#     return {
#         'statusCode': 200,
#         'headers': {
#             'Content-Type': 'text/plain'
#         },
#         'body': 'Hello, CDK! You have hit {}\n'.format(event['path'])
#     }

# @app.get("/")
# async def root():
#     return {"message": "Hello from Ordering API!"}

# @app.get("/")
# async def root(request: Request):
#     return {"aws": request.scope["aws"]}

@app.get("/")
async def root(request: Request):
  print(request)
  print(request.query_params)
  return {"message": "Hello from Ordering API!"}

# Create Order

# Get order by username and orderID

# TODO
# Get all orders by username

# Get Orders by range and username

# get 
def _get_table():
    table_name = os.environ.get("ORDERING_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
